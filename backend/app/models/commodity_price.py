from datetime import datetime

from sqlalchemy import UniqueConstraint, DateTime, String, Integer, Float, BigInteger, Date, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base

class CommodityPrice(Base):
    __tablename__ = "trn_commodity_price"
    __table_args__ = (
        UniqueConstraint("commodity_id", "date", name="uq_trn_commodity_price_code_market_date"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, index=True)
    commodity_id: Mapped[int] = mapped_column(Integer, ForeignKey("mst_commodities.id"), nullable=False, index=True)
    commodity_code: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    commodity_market: Mapped[str] = mapped_column(String(32), nullable=True, index=True)
    date: Mapped[datetime.date] = mapped_column(Date, nullable=False, index=True)
    open: Mapped[float | None] = mapped_column(Float, nullable=True)
    high: Mapped[float | None] = mapped_column(Float, nullable=True)
    low: Mapped[float | None] = mapped_column(Float, nullable=True)
    close: Mapped[float | None] = mapped_column(Float, nullable=True)
    adj_close: Mapped[float | None] = mapped_column(Float, nullable=True)
    volume: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )