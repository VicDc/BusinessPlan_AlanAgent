from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # LLM
    LLM_BASE_URL: str = "http://localhost:1234/v1"
    LLM_MODEL: str = "gemma-4-26b"
    LLM_PROVIDER: str = "local"   # "local" | "claude_fast" | "claude_quality"
    ANTHROPIC_API_KEY: str = ""

    # Web search
    SERPER_API_KEY: str = ""

    # Output
    OUTPUT_DIR: str = "output"

    # App
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    LOG_LEVEL: str = "INFO"

    # Orchestrator
    MAX_REVISION_CYCLES: int = 3


settings = Settings()
