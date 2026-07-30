import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    api_key: str
    base_url: str
    model: str
    max_iterations: int


def load_settings(
    model_override: str | None = None,
    base_url_override: str | None = None,
    max_iterations_override: int | None = None,
) -> Settings:
    api_key = (
        os.getenv("AI_AGENT_API_KEY")
        or os.getenv("OPENROUTER_API_KEY")
    )

    if not api_key:
        raise RuntimeError(
            "No API key was found. Set AI_AGENT_API_KEY "
            "or OPENROUTER_API_KEY in your .env file."
        )

    base_url = (
        base_url_override
        or os.getenv("AI_AGENT_BASE_URL")
        or "https://openrouter.ai/api/v1"
    )

    model = (
        model_override
        or os.getenv("AI_AGENT_MODEL")
        or "openrouter/free"
    )

    max_iterations = (
        max_iterations_override
        or int(os.getenv("AI_AGENT_MAX_ITERATIONS", "20"))
    )

    return Settings(
        api_key=api_key,
        base_url=base_url,
        model=model,
        max_iterations=max_iterations,
    )
