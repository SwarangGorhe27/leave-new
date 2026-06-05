from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "HRMS AI Service"
    debug: bool = False
    jwt_secret: str = "change-this-to-a-secure-secret-key"
    jwt_algorithm: str = "HS256"
    backend_url: str = "http://backend:8000"
    model_provider: str = "openai"  # openai | azure | ollama
    openai_api_key: str = ""

    class Config:
        env_prefix = "AI_"
        env_file = ".env"


settings = Settings()
