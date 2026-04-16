import datetime as dt
from datetime import datetime

from sqlalchemy import BigInteger, Date, DateTime, Float, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class WhiteList(Base):
    __tablename__ = "trn_white_list"

    market: Mapped[str] = mapped_column(String(64), primary_key=True, nullable=False)
    code: Mapped[str] = mapped_column(String(16), primary_key=True, nullable=False)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    sector_id: Mapped[int] = mapped_column(BigInteger, nullable=True)
    summary: Mapped[str] = mapped_column(String(256), nullable=True)
    currency: Mapped[str] = mapped_column(String(16), nullable=True)
    is_etf: Mapped[bool] = mapped_column(nullable=True)
    trading_unit: Mapped[int] = mapped_column(BigInteger, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
