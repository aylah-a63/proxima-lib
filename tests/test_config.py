from proxima_lib.config import Config, save_config, load_config
from unittest.mock import patch


def test_config_roundtrip(tmp_path):
    with patch("proxima_lib.config.config_dir", return_value=tmp_path):
        cfg = Config(
            active_personas=["aria"],
            channels={"111": "aria"},
            persona_tokens={"aria": "aria-token"},
        )
        save_config(cfg)
        loaded = load_config()

    assert loaded.active_personas == ["aria"]
    assert loaded.channels == {"111": "aria"}
    assert loaded.persona_tokens == {"aria": "aria-token"}


def test_config_defaults_when_missing(tmp_path):
    with patch("proxima_lib.config.config_dir", return_value=tmp_path):
        cfg = load_config()
    assert cfg.active_personas == []
    assert cfg.channels == {}
