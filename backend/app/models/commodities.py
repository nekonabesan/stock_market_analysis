from datetime import datetime

from sqlalchemy import DateTime, String, Integer, func, UniqueConstraint, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base

class Commodities(Base):
    __tablename__ = "mst_commodities"
    __table_args__ = (
        UniqueConstraint("code", "market", name="uq_commodities_code_market"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, index=True)
    code: Mapped[str] = mapped_column(String(16), nullable=False)
    market: Mapped[str | None] = mapped_column(String(64), nullable=True)
    currency_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("mst_currency.id"), nullable=True)
    name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    sector: Mapped[str | None] = mapped_column(String(128), nullable=True)
    memo: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )