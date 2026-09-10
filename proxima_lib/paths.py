import sys
from pathlib import Path


def config_dir() -> Path:
    if sys.platform == "darwin":
        p = Path.home() / "Library" / "Application Support" / "proxima"
    elif sys.platform == "win32":
        import os
        p = Path(os.environ["APPDATA"]) / "proxima"
    else:
        p = Path.home() / ".config" / "proxima"
    p.mkdir(parents=True, exist_ok=True)
    return p


def data_dir() -> Path:
    if sys.platform == "darwin":
        p = Path.home() / "Library" / "Application Support" / "proxima"
    elif sys.platform == "win32":
        import os
        p = Path(os.environ["APPDATA"]) / "proxima"
    else:
        p = Path.home() / ".local" / "share" / "proxima"
    p.mkdir(parents=True, exist_ok=True)
    return p
