import json
import os
from typing import List, Optional

from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

DEFAULT_CORS_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
]


def _parse_cors_origins(raw: Optional[str]) -> List[str]:
    """
    Parses the CORS_ORIGINS environment variable.
    Accepts either a JSON array (["http://localhost:5173"]) or a
    comma-separated string ("http://localhost:5173,http://localhost:3000").
    Falls back to the default development origins when unset or invalid.
    """
    if not raw or not raw.strip():
        return list(DEFAULT_CORS_ORIGINS)
    raw = raw.strip()
    try:
        parsed = json.loads(raw)
        if isinstance(parsed, list):
            return [str(o).strip().rstrip("/") for o in parsed if str(o).strip()]
    except json.JSONDecodeError:
        pass
    return [o.strip().rstrip("/") for o in raw.split(",") if o.strip()]


def _parse_bool(raw: Optional[str], default: bool = True) -> bool:
    if raw is None or not raw.strip():
        return default
    return raw.strip().lower() in ("true", "1", "yes", "on")


class Settings(BaseModel):
    app_name: str = os.getenv("APP_NAME", "NetSage AI Backend")
    debug: bool = _parse_bool(os.getenv("DEBUG"), default=True)
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./netsage.db")
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    cors_origins: List[str] = _parse_cors_origins(os.getenv("CORS_ORIGINS"))
    max_payload_size_bytes: int = 5 * 1024 * 1024  # 5MB

settings = Settings()
