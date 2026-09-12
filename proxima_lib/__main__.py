import sys
import asyncio


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "encrypt":
        _encrypt_cmd(sys.argv[2:])
    else:
        from proxima_lib.bot import run
        asyncio.run(run())


def _encrypt_cmd(paths: list[str]) -> None:
    from pathlib import Path
    from proxima_lib.crypto import MAGIC, encrypt_per
    from proxima_lib.persona import parse_per_plaintext, validate_safety_block

    if not paths:
        print("Usage: python -m proxima_lib encrypt <file.per> [...]", file=sys.stderr)
        sys.exit(1)

    for p in paths:
        path = Path(p)
        raw = path.read_bytes()
        if raw[:4] == MAGIC:
            print(f"{path}: already encrypted, skipping")
            continue
        pf = parse_per_plaintext(path)
        if not validate_safety_block(pf.system_prompt):
            print(f"{path}: missing safety block — refusing to encrypt", file=sys.stderr)
            sys.exit(1)
        path.write_bytes(encrypt_per(raw))
        print(f"{path}: encrypted")


if __name__ == "__main__":
    main()
