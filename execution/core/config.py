"""Global application configuration and environment settings."""

from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


_BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):
    """Central configuration for Sanctum."""

    model_config = SettingsConfigDict(
        env_file=str(_BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Base Paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    TEMP_DIR: Path = BASE_DIR / ".tmp"
    OBSIDIAN_VAULT_PATH: Optional[Path] = None

    # Local LLM (Ollama)
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    DEFAULT_REASONING_MODEL: str = "qwen2.5:7b"
    DEFAULT_FAST_MODEL: str = "qwen2.5:1.5b"
    RESEARCH_REASONING_MODEL: str = "deepseek-r1:7b"
    DEFAULT_EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    LLM_TEMPERATURE: float = 0.2
    LLM_TIMEOUT_SECONDS: float = 60.0

    # Optional Cloud API Keys for instant high-intelligence fallback
    GEMINI_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    GROQ_API_KEY: Optional[str] = None
    OPENAI_BASE_URL: Optional[str] = None

    # ML & RAG Configuration
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333
    QDRANT_PATH: Optional[Path] = BASE_DIR / ".tmp" / "qdrant_storage"
    RAG_TOP_K: int = 20
    RAG_RERANK_TOP_N: int = 3
    TEMPORAL_DECAY_HALF_LIFE_DAYS: float = 14.0

    # SQLite State & Checkpointing
    SQLITE_DB_PATH: Path = BASE_DIR / ".tmp" / "personal_ai_os.db"

    # API Server
    API_HOST: str = "127.0.0.1"
    API_PORT: int = 8000
    DEBUG: bool = False

    # Security & Permissions
    REQUIRE_APPROVAL_FOR_HIGH_RISK: bool = True
    AUTO_APPROVE_LOW_RISK: bool = True


# Global settings singleton
settings = Settings()
