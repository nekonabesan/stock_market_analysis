from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class IndexDefinition(BaseModel):
    name: str
    code: str
    market: str
    region: str


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


# Index definitions
INDICES: List[IndexDefinition] = [
    IndexDefinition(name="日経平均", code="^N225", market="TSE", region="JP"),
    IndexDefinition(name="S&P 500", code="^GSPC", market="NYSE", region="US"),
    IndexDefinition(name="Dow Jones", code="^DJI", market="NYSE", region="US"),
    IndexDefinition(name="DAX", code="^GDAXI", market="FRA", region="DE"),
    IndexDefinition(name="CAC 40", code="^FCHI", market="EPA", region="FR"),
    IndexDefinition(name="FTSE 100", code="^FTSE", market="LSE", region="GB"),
    IndexDefinition(name="ハンセン指数", code="^HSI", market="HKEX", region="HK"),
]


settings = Settings()
