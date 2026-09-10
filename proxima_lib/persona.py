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
        if stripped.upper().startswith("FROM "):
            from_model = stripped[5:].strip()
        elif stripped.upper().startswith("TOKEN_NAME "):
            token_name = stripped[11:].strip()
        elif stripped.upper().startswith('SYSTEM """'):
            in_system = True
            rest = stripped[10:]
            if rest:
                system_lines.append(rest)
        elif in_system:
            if stripped == '"""':
                in_system = False
            else:
                system_lines.append(line)
        elif stripped.upper().startswith("PARAMETER "):
            parts = stripped[10:].split(None, 1)
            if len(parts) == 2:
                parameters[parts[0]] = parts[1]

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
    return system_prompt.strip().startswith(SAFETY_BLOCK)
