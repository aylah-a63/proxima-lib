import sys
from pathlib import Path


def config_dir() -> Path:
    if sys.platform == "darwin":
        p = Path.home() / "Library" / "Application Support" / "proxima"
    elif sys.platform == "win32":
        import os
        appdata = os.environ.get("APPDATA") or str(Path.home() / "AppData" / "Roaming")
        p = Path(appdata) / "proxima"
    else:
        p = Path.home() / ".config" / "proxima"
    p.mkdir(parents=True, exist_ok=True)
    return p


def personas_dir() -> Path:
    p = config_dir() / "personas"
    p.mkdir(parents=True, exist_ok=True)
    return p


def data_dir() -> Path:
    if sys.platform == "darwin":
        p = Path.home() / "Library" / "Application Support" / "proxima"
    elif sys.platform == "win32":
        import os
        appdata = os.environ.get("APPDATA") or str(Path.home() / "AppData" / "Roaming")
        p = Path(appdata) / "proxima"
    else:
        p = Path.home() / ".local" / "share" / "proxima"
    p.mkdir(parents=True, exist_ok=True)
    return p
