from functools import lru_cache
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


ROOT_DIR = Path(__file__).resolve().parents[2]
BACKEND_DIR = Path(__file__).resolve().parents[1]


class Settings(BaseSettings):
    app_name: str = "JIRACHI"
    environment: str = "development"
    demo_mode: bool = False
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/jirachi"
    supabase_url: str = ""
    supabase_anon_key: str = ""
    gemini_api_key: str = ""
    admin_token: str = ""
    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    @property
    def cors_origin_regex(self) -> str | None:
        if self.environment != "development":
            return None

        return r"^http://(localhost|127\.0\.0\.1|0\.0\.0\.0|172\.\d+\.\d+\.\d+):5173$"

    @field_validator("database_url")
    @classmethod
    def validate_database_url(cls, value: str) -> str:
        if not value.startswith("postgresql+asyncpg://"):
            raise ValueError("DATABASE_URL must start with postgresql+asyncpg://")

        # asyncpg expects `ssl`, not libpq's `sslmode`, and does not accept
        # `channel_binding` as a direct connect() keyword.
        parsed = urlsplit(value)
        query_params = dict(parse_qsl(parsed.query, keep_blank_values=True))
        if "sslmode" in query_params and "ssl" not in query_params:
            query_params["ssl"] = query_params.pop("sslmode")
        query_params.pop("channel_binding", None)

        normalized_query = urlencode(query_params, doseq=True)
        value = urlunsplit(
            (parsed.scheme, parsed.netloc, parsed.path, normalized_query, parsed.fragment)
        )
        return value

    model_config = SettingsConfigDict(
        env_file=(ROOT_DIR / ".env", BACKEND_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
