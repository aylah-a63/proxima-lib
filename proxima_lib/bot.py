import os
import sys
import asyncio
import discord
from datetime import datetime, timezone
from proxima_lib.config import load_config
from proxima_lib.db import Database
from proxima_lib.ollama_client import OllamaClient
from proxima_lib.paths import personas_dir
from proxima_lib.persona import PersonaFile, parse_per_file, validate_safety_block
from proxima_lib.router import Router


class BotInstance(discord.Client):
    def __init__(self, token: str, personas: dict[str, PersonaFile], router: Router,
                 ollama: OllamaClient, db: Database, config):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(intents=intents)
        self._token = token
        self._personas = personas
        self._router = router
        self._ollama = ollama
        self._db = db
        self._config = config

    async def on_ready(self):
        print(f"proxima-lib: logged in as {self.user}")

    async def on_message(self, message: discord.Message):
        if message.author == self.user:
            return
        channel_id = str(message.channel.id)
        persona = self._router.route(channel_id)
        if persona is None:
            await message.channel.send(self._config.default_reject_message)
            return
        if persona not in self._personas:
            print(f"[proxima] channel {channel_id} routed to '{persona}' but this instance owns {set(self._personas)} — skipping")
            return

        persona_file = self._personas[persona]
        try:
            response = await self._ollama.generate(
                model=persona,
                user_message=message.content,
                system=persona_file.system_prompt,
            )
        except Exception as e:
            print(f"[OLLAMA_UNAVAILABLE] {e}", file=sys.stderr)
            response = self._config.ollama_error_message
            prompt_content = "[OLLAMA_UNAVAILABLE]"
        else:
            prompt_content = message.content

        await self._db.insert_message(
            message_id=str(message.id),
            channel_id=channel_id,
            user_id=str(message.author.id),
            username=str(message.author.name),
            nickname=message.author.display_name or None,
            message_content=message.content,
            prompt_content=prompt_content,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
        await message.channel.send(response)

    async def on_message_delete(self, message: discord.Message):
        await self._db.mark_deleted(str(message.id))

    async def start_bot(self):
        await self.start(self._token)


async def run() -> None:
    config = load_config()
    db = await Database.create()
    ollama = OllamaClient()
    await ollama.health_check()
    router = Router(config)

    # Load and validate every active persona's .per file.
    pdir = personas_dir()
    all_personas: dict[str, PersonaFile] = {}
    for name in config.active_personas:
        per_path = pdir / f"{name}.per"
        if not per_path.exists():
            raise RuntimeError(f"Persona file not found: {per_path}")
        pf = parse_per_file(per_path)
        if not validate_safety_block(pf.system_prompt):
            raise RuntimeError(f"Persona '{name}' missing required safety block — re-register with `proxima-sh persona create`")
        all_personas[name] = pf

    # Group personas by their token env var.
    # persona_tokens maps persona_name -> keychain entry name;
    # proxima-sh injects PROXIMA_TOKEN_<NAME> or DISCORD_TOKEN.
    token_to_personas: dict[str, dict[str, PersonaFile]] = {}
    for name, pf in all_personas.items():
        token_key = config.persona_tokens.get(name)
        if token_key:
            env_var = f"PROXIMA_TOKEN_{token_key.upper()}"
            token = os.environ.get(env_var)
            if not token:
                raise RuntimeError(f"Expected env var {env_var} for persona '{name}'")
        else:
            token = os.environ.get("DISCORD_TOKEN")
            if not token:
                raise RuntimeError("Expected env var DISCORD_TOKEN")
        token_to_personas.setdefault(token, {})[name] = pf

    bots = [
        BotInstance(token, personas, router, ollama, db, config)
        for token, personas in token_to_personas.items()
    ]

    await asyncio.gather(*(bot.start_bot() for bot in bots))
