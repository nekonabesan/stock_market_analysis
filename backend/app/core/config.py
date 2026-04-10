from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", ".env.local"),
        env_file_encoding="utf-8",
    )

    database_url: str = "postgresql://postgres:postgres@db:5432/stock_market"
    api_prefix: str = "/api/v1"
    app_name: str = "Stock Market Analysis API"
    app_env: str = "local"
    log_level: str = "INFO"
    log_sink: str = "stdout"
    log_serialize: bool = False


settings = Settings()
