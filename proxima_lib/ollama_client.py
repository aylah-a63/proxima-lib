import ollama


class OllamaClient:
    def __init__(self, host: str = "http://localhost:11434"):
        self._host = host
        self._client = ollama.AsyncClient(host=host)

    async def health_check(self) -> None:
        try:
            await self._client.list()
        except Exception as e:
            raise RuntimeError(
                f"Ollama is not reachable at {self._host} — is it running? ({e})"
            ) from e

    async def generate(self, model: str, user_message: str, system: str | None = None) -> str:
        response = await self._client.generate(model=model, prompt=user_message, system=system)
        return response.response
