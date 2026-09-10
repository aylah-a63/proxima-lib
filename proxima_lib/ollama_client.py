import ollama


class OllamaClient:
    def __init__(self, host: str = "http://localhost:11434"):
        self._client = ollama.AsyncClient(host=host)

    async def health_check(self) -> None:
        try:
            await self._client.list()
        except Exception as e:
            raise RuntimeError(
                f"Ollama is not reachable at localhost:11434 — is it running? ({e})"
            ) from e

    async def generate(self, model: str, user_message: str) -> str:
        response = await self._client.generate(model=model, prompt=user_message)
        return response["response"]
