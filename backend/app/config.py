from pydantic_settings import BaseSettings
from typing import Optional
import json
import os


class Settings(BaseSettings):
    # API配置
    openai_api_key: str
    openai_api_base: str | None = None
    openai_model: str = "gpt-3.5-turbo"
    secret_key: str = "dev-secret-key-change-in-production"
    
    # JWT配置
    jwt_algorithm: str = "HS256"
    jwt_expire_hours: int = 24 * 7
    
    # 数据库配置
    database_url: str = "sqlite:///./data/notes.db"  # 改为 data 目录
    
    # CORS配置
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:5173"]
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 如果 CORS_ORIGINS 是 JSON 字符串，解析它
        cors_origins_env = os.getenv("CORS_ORIGINS")
        if cors_origins_env:
            try:
                parsed = json.loads(cors_origins_env)
                if isinstance(parsed, list):
                    self.cors_origins = parsed
            except (json.JSONDecodeError, ValueError):
                if "," in cors_origins_env:
                    self.cors_origins = [origin.strip() for origin in cors_origins_env.split(",")]
                else:
                    self.cors_origins = [cors_origins_env.strip()]


settings = Settings()