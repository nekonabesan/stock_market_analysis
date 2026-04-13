from pydantic import BaseModel, model_validator


class SearchRequest(BaseModel):
    market: str
    name: str | None = None
    code: str | None = None

    @model_validator(mode="after")
    def validate_name_or_code(self):
        normalized_name = self.name.strip() if self.name else ""
        normalized_code = self.code.strip() if self.code else ""
        if not normalized_name and not normalized_code:
            raise ValueError("Either name or code is required")

        self.name = normalized_name or None
        self.code = normalized_code or None
        self.market = self.market.strip().upper()
        return self


class SearchResponse(BaseModel):
    found: bool
    market: str
    name: str | None = None
    code: str
