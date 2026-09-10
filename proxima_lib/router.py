from proxima_lib.config import Config


class Router:
    def __init__(self, config: Config):
        self._config = config

    def route(self, channel_id: str) -> str | None:
        if channel_id in self._config.channels:
            return self._config.channels[channel_id]
        if len(self._config.active_personas) == 1:
            return self._config.active_personas[0]
        return None
