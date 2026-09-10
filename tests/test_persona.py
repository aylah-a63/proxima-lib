from pathlib import Path
import pytest
import textwrap
from proxima_lib.persona import (
    parse_per_file, validate_safety_block, SAFETY_BLOCK, PersonaFile
)


VALID_PER = textwrap.dedent("""\
    FROM llama3.2
    TOKEN_NAME aria-token

    SYSTEM \"\"\"
    {safety}

    ---

    You are Aria, a helpful assistant.
    \"\"\"

    PARAMETER temperature 0.8
    PARAMETER top_p 0.9
""").format(safety=SAFETY_BLOCK)


def test_parse_valid(tmp_path):
    f = tmp_path / "aria.per"
    f.write_text(VALID_PER)
    p = parse_per_file(f)
    assert p.from_model == "llama3.2"
    assert p.token_name == "aria-token"
    assert "You are Aria" in p.system_prompt
    assert p.parameters["temperature"] == "0.8"
    assert p.parameters["top_p"] == "0.9"


def test_parse_no_from_raises(tmp_path):
    f = tmp_path / "bad.per"
    f.write_text('SYSTEM """\nhello\n"""\n')
    with pytest.raises(ValueError, match="FROM"):
        parse_per_file(f)


def test_validate_safety_block_present():
    assert validate_safety_block(SAFETY_BLOCK + "\n\n---\n\nHello") is True


def test_validate_safety_block_absent():
    assert validate_safety_block("You are a helpful bot.") is False


def test_validate_safety_block_tampered():
    tampered = SAFETY_BLOCK.replace("hateful", "great")
    assert validate_safety_block(tampered + "\n\n---\n\nHello") is False
