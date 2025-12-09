from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # API配置
    openai_api_key: str
    openai_api_base: str | None = None  # 可选：自定义API Base URL（如DashScope）
    openai_model: str = "gpt-3.5-turbo"  # 模型名称（如 gpt-3.5-turbo, qwen-plus 等）
    secret_key: str = "dev-secret-key-change-in-production"
    
    # JWT配置
    jwt_algorithm: str = "HS256"
    jwt_expire_hours: int = 24 * 7  # 默认7天过期
    
    # 数据库配置
    database_url: str = "sqlite:///./notes.db"
    
    # CORS配置
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:5173"]
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

