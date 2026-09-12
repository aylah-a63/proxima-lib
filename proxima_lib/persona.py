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


def parse_per_file(path: Path) -> PersonaFile:
    text = path.read_text(encoding="utf-8")
    from_model = None
    token_name = None
    system_lines: list[str] = []
    parameters: dict[str, str] = {}

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
        name=path.stem,
        from_model=from_model,
        system_prompt="\n".join(system_lines).strip(),
        parameters=parameters,
        token_name=token_name,
    )


def validate_safety_block(system_prompt: str) -> bool:
    return system_prompt.startswith(SAFETY_BLOCK)
