from datetime import date as dt_date, datetime

from sqlalchemy import Date, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class IncomeStatement(Base):
    __tablename__ = "trn_income_stmt"

    date: Mapped[dt_date] = mapped_column(Date, primary_key=True, nullable=False)
    market: Mapped[str | None] = mapped_column(String(64), nullable=True)
    code: Mapped[str] = mapped_column(String(16), primary_key=True, nullable=False)
    revenue: Mapped[float | None] = mapped_column(nullable=True)
    earnings: Mapped[float] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    
    