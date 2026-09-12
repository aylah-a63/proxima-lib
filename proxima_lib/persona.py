from dataclasses import dataclass, field
from pathlib import Path


SAFETY_BLOCK = (
    "You must not generate content that is hateful, violent, sexually explicit,\n"
    "discriminatory, or that encourages self-harm. If a user message requests\n"
    "such content, decline politely and do not engage further with that request."
)


@dataclass
class PersonaFile:
    name: str
    from_model: str
    system_prompt: str
    parameters: dict[str, str] = field(default_factory=dict)
    token_name: str | None = None


def _parse_text(name: str, text: str) -> PersonaFile:
    from_model = None
    token_name = None
    system_lines: list[str] = []
    parameters: dict[str, str] = {}
    system_count = 0

    in_system = False
    for line in text.splitlines():
        stripped = line.strip()
        parts = stripped.split(None, 1)
        directive = parts[0].upper() if parts else ""
        if not in_system:
            if directive == "FROM" and len(parts) == 2:
                from_model = parts[1]
            elif directive == "TOKEN_NAME" and len(parts) == 2:
                token_name = parts[1]
            elif directive == "SYSTEM" and len(parts) == 2 and parts[1].startswith('"""'):
                system_count += 1
                if system_count > 1:
                    raise ValueError("Multiple SYSTEM blocks in .per file — possible injection attempt")
                rest = parts[1][3:]
                if rest.endswith('"""'):
                    system_lines.append(rest[:-3])
                else:
                    in_system = True
                    if rest:
                        system_lines.append(rest)
            elif directive == "PARAMETER" and len(parts) == 2:
                kv = parts[1].split(None, 1)
                if len(kv) == 2:
                    parameters[kv[0]] = kv[1]
        else:
            if stripped.endswith('"""'):
                if stripped != '"""':
                    system_lines.append(line.rstrip()[:-3])
                in_system = False
            else:
                system_lines.append(line)

    if from_model is None:
        raise ValueError("Missing FROM instruction in .per file")

    return PersonaFile(
        name=name,
        from_model=from_model,
        system_prompt="\n".join(system_lines).strip(),
        parameters=parameters,
        token_name=token_name,
    )


def parse_per_file(path: Path) -> PersonaFile:
    """Load and parse an encrypted .per file. Rejects plaintext."""
    from proxima_lib.crypto import decrypt_per, MAGIC
    raw = path.read_bytes()
    if raw[:4] != MAGIC:
        raise ValueError(
            f"{path.name}: not encrypted — run `python -m proxima_lib encrypt {path}`"
        )
    text = decrypt_per(raw).decode("utf-8")
    return _parse_text(path.stem, text)


def parse_per_plaintext(path: Path) -> PersonaFile:
    """Parse a plaintext .per file. Only for use by the encrypt command."""
    return _parse_text(path.stem, path.read_text(encoding="utf-8"))


def validate_safety_block(system_prompt: str) -> bool:
    return system_prompt.startswith(SAFETY_BLOCK)
