import datetime as dt
from datetime import datetime

from sqlalchemy import BigInteger, Date, DateTime, Float, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class StockPrice(Base):
    __tablename__ = "trn_stock_price"
    __table_args__ = (
        UniqueConstraint("stock_code", "stock_market", "date", name="uq_trn_stock_price_code_market_date"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    stock_code: Mapped[str] = mapped_column(String(16), nullable=False, index=True)
    stock_market: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    date: Mapped[dt.date] = mapped_column(Date, nullable=False, index=True)
    open: Mapped[float | None] = mapped_column(Float, nullable=True)
    high: Mapped[float | None] = mapped_column(Float, nullable=True)
    low: Mapped[float | None] = mapped_column(Float, nullable=True)
    close: Mapped[float | None] = mapped_column(Float, nullable=True)
    volume: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    ma5: Mapped[float | None] = mapped_column(Float, nullable=True)  # 5日移動平均
    ma25: Mapped[float | None] = mapped_column(Float, nullable=True)  # 25日移動平均
    ma75: Mapped[float | None] = mapped_column(Float, nullable=True)  # 75日移動平均
    upper2: Mapped[float | None] = mapped_column(Float, nullable=True)  # ボリンジャーバンド　 +2σ
    lower2: Mapped[float | None] = mapped_column(Float, nullable=True)  # ボリンジャーバンド -2σ
    macd: Mapped[float | None] = mapped_column(Float, nullable=True)  # MACD
    macd_signal: Mapped[float | None] = mapped_column(Float, nullable=True)  # Signal
    hist: Mapped[float | None] = mapped_column(Float, nullable=True)  # ヒストグラム
    rsi14: Mapped[float | None] = mapped_column(Float, nullable=True)  # RSI14
    rsi28: Mapped[float | None] = mapped_column(Float, nullable=True)  # RSI28
    rci9: Mapped[float | None] = mapped_column(Float, nullable=True)  # RCI9
    rci26: Mapped[float | None] = mapped_column(Float, nullable=True)  # RCI26
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
