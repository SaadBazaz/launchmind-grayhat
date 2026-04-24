import json
from dotenv import load_dotenv
from agents.llm_provider import LLMProvider, get_provider

load_dotenv()


def _strip_fences(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        text = text.split("```", 2)[1]
        if text.startswith("json"):
            text = text[4:]
        text = text.rsplit("```", 1)[0].strip()
    return text


class BaseAgent:
    """Base class for all LaunchMind agents. Provides LLM access and structured logging."""

    def __init__(self, name: str, provider: LLMProvider = None):
        self.name = name
        self._provider = provider or get_provider()

    def log(self, msg: str) -> None:
        print(f"[{self.name.upper()}] {msg}")

    def call_llm(self, system: str, user: str, max_tokens: int = 2000, json_mode: bool = False) -> str:
        self.log(f"LLM call → {user[:80]}...")
        return self._provider.complete(system, user, max_tokens, json_mode=json_mode)

    def call_llm_json(self, system: str, user: str, max_tokens: int = 2000) -> dict:
        """LLM call that parses and returns JSON. Uses json_mode for structured output."""
        raw = self.call_llm(system, user, max_tokens, json_mode=True)
        text = _strip_fences(raw)
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            self.log("JSON parse failed, retrying...")
            raw2 = self.call_llm(
                system + " IMPORTANT: Return ONLY raw JSON with no markdown formatting.",
                user,
                max_tokens,
                json_mode=True,
            )
            return json.loads(_strip_fences(raw2))
