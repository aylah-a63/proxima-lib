import tomllib
import tomli_w
from dataclasses import dataclass, field
from proxima_lib.paths import config_dir


@dataclass
class Config:
    python_cmd: str = "python3"
    default_reject_message: str = "I'm not set up to respond here."
    ollama_error_message: str = "I'm having trouble thinking right now."
    ollama_host: str = "http://localhost:11434"
    active_personas: list[str] = field(default_factory=list)
    channels: dict[str, str] = field(default_factory=dict)
    persona_tokens: dict[str, str] = field(default_factory=dict)
    allowed_guilds: list[str] = field(default_factory=list)
    allowed_channels: list[str] = field(default_factory=list)


def load_config() -> Config:
    path = config_dir() / "config.toml"
    if not path.exists():
        return Config()
    with open(path, "rb") as f:
        data = tomllib.load(f)
    bot = data.get("bot", {})
    return Config(
        python_cmd=bot.get("python_cmd", "python3"),
        default_reject_message=bot.get("default_reject_message", "I'm not set up to respond here."),
        ollama_error_message=bot.get("ollama_error_message", "I'm having trouble thinking right now."),
        ollama_host=data.get("ollama", {}).get("host", "http://localhost:11434"),
        active_personas=data.get("personas", {}).get("active", []),
        channels=data.get("channels", {}),
        persona_tokens=data.get("persona_tokens", {}),
        allowed_guilds=data.get("whitelist", {}).get("guilds", []),
        allowed_channels=data.get("whitelist", {}).get("channels", []),
    )


def save_config(config: Config) -> None:
    path = config_dir() / "config.toml"
    data = {
        "bot": {
            "python_cmd": config.python_cmd,
            "default_reject_message": config.default_reject_message,
            "ollama_error_message": config.ollama_error_message,
        },
        "ollama": {"host": config.ollama_host},
        "personas": {"active": config.active_personas},
        "channels": config.channels,
        "persona_tokens": config.persona_tokens,
        "whitelist": {
            "guilds": config.allowed_guilds,
            "channels": config.allowed_channels,
        },
    }
    tmp = path.with_suffix(".toml.tmp")
    with open(tmp, "wb") as f:
        tomli_w.dump(data, f)
    tmp.replace(path)
