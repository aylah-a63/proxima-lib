from proxima_lib.config import Config
from proxima_lib.router import Router


def test_route_mapped_channel():
    cfg = Config(channels={"111": "aria"}, active_personas=["aria"])
    router = Router(cfg)
    assert router.route("111") == "aria"


def test_route_unmapped_channel_single_active():
    cfg = Config(channels={}, active_personas=["aria"])
    router = Router(cfg)
    assert router.route("999") == "aria"


def test_route_unmapped_channel_no_active():
    cfg = Config(channels={}, active_personas=[])
    router = Router(cfg)
    assert router.route("999") is None


def test_route_unmapped_channel_multiple_active_returns_none():
    cfg = Config(channels={}, active_personas=["aria", "bob"])
    router = Router(cfg)
    assert router.route("999") is None


def test_route_mapped_takes_priority_over_single_active():
    cfg = Config(channels={"111": "aria"}, active_personas=["bob"])
    router = Router(cfg)
    assert router.route("111") == "aria"
