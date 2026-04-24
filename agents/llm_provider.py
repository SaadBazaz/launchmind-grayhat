import os
import time
import requests
import anthropic
from google import genai
from abc import ABC, abstractmethod


class LLMProvider(ABC):
    @abstractmethod
    def complete(self, system: str, user: str, max_tokens: int = 2000, json_mode: bool = False) -> str:
        ...


class AnthropicProvider(LLMProvider):
    MODEL = "claude-sonnet-4-6"

    def __init__(self):
        self._client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    def complete(self, system: str, user: str, max_tokens: int = 2000, json_mode: bool = False) -> str:
        resp = self._client.messages.create(
            model=self.MODEL,
            max_tokens=max_tokens,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
        return resp.content[0].text


class DeepSeekProvider(LLMProvider):
    BASE_URL = "https://api.deepseek.com/chat/completions"
    MODEL = "deepseek-chat"

    def __init__(self):
        self._api_key = os.environ["DEEPSEEK_API_KEY"]

    def complete(self, system: str, user: str, max_tokens: int = 2000, json_mode: bool = False) -> str:
        resp = requests.post(
            self.BASE_URL,
            headers={
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": self.MODEL,
                "max_tokens": max_tokens,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
            },
            timeout=60,
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]


class GeminiProvider(LLMProvider):
    MODEL = "gemini-2.0-flash-lite"
    _RETRY_DELAYS = [30, 60, 120]

    def __init__(self):
        self._client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

    def complete(self, system: str, user: str, max_tokens: int = 2000, json_mode: bool = False) -> str:
        from google.genai import types
        from google.genai.errors import ClientError

        config = types.GenerateContentConfig(
            system_instruction=system,
            max_output_tokens=max_tokens,
        )
        for attempt, delay in enumerate([0] + self._RETRY_DELAYS):
            if delay:
                print(f"[GEMINI] Rate limited — retrying in {delay}s (attempt {attempt + 1})...")
                time.sleep(delay)
            try:
                resp = self._client.models.generate_content(
                    model=self.MODEL,
                    contents=user,
                    config=config,
                )
                return resp.text
            except ClientError as e:
                if e.status == 429 and attempt < len(self._RETRY_DELAYS):
                    continue
                raise


class OllamaProvider(LLMProvider):
    BASE_URL = "http://localhost:11434/api/chat"
    MODEL = "qwen2.5:1.5b"

    def complete(self, system: str, user: str, max_tokens: int = 2000, json_mode: bool = False) -> str:
        body = {
            "model": self.MODEL,
            "stream": False,
            "options": {"num_predict": max_tokens},
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        }
        if json_mode:
            body["format"] = "json"
        resp = requests.post(self.BASE_URL, json=body, timeout=120)
        resp.raise_for_status()
        return resp.json()["message"]["content"]


_PROVIDERS = {
    "anthropic": AnthropicProvider,
    "deepseek": DeepSeekProvider,
    "gemini": GeminiProvider,
    "ollama": OllamaProvider,
}


def get_provider(name: str = None) -> LLMProvider:
    """Return provider instance. Reads LLM_PROVIDER env var if name not given."""
    key = (name or os.environ.get("LLM_PROVIDER", "ollama")).lower()
    cls = _PROVIDERS.get(key)
    if cls is None:
        raise ValueError(f"Unknown LLM provider '{key}'. Choose: {list(_PROVIDERS)}")
    return cls()
