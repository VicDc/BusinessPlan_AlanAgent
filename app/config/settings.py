from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # LLM
    LLM_BASE_URL: str = "http://localhost:1234/v1"
    LLM_MODEL: str = "gemma-4-26b"
    LLM_PROVIDER: str = "local"   # "local" | "claude_fast" | "claude_quality"
    ANTHROPIC_API_KEY: str = ""

    # Web search
    SERPER_API_KEY: str = ""

    # Output
    OUTPUT_DIR: str = "output"

    # Redis (opzionale)
    REDIS_URL: str = "redis://localhost:6379/0"

    # App
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    LOG_LEVEL: str = "INFO"

    # Orchestrator
    MAX_REVISION_CYCLES: int = 3

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
