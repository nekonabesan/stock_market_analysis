from datetime import date, datetime

from sqlalchemy import Date, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class CashFlow(Base):
    __tablename__ = "trn_cash_flow"

    date: Mapped[date] = mapped_column(Date, primary_key=True)
    market: Mapped[str | None] = mapped_column(String(64), nullable=True)
    code: Mapped[str] = mapped_column(String(16), primary_key=True, nullable=False)
    free_cash_flow: Mapped[float] = mapped_column(nullable=True)
    repurchase_of_capital_stock: Mapped[float] = mapped_column(nullable=True)
    repayment_of_debt: Mapped[float] = mapped_column(nullable=True)
    issuance_of_debt: Mapped[float] = mapped_column(nullable=True)
    capital_expenditure: Mapped[float] = mapped_column(nullable=True)
    end_cash_position: Mapped[float] = mapped_column(nullable=True)
    beginning_cash_position: Mapped[float] = mapped_column(nullable=True)
    effect_of_exchange_rate_changes: Mapped[float] = mapped_column(nullable=True)
    changes_in_cash: Mapped[float] = mapped_column(nullable=True)
    financing_cash_flow: Mapped[float] = mapped_column(nullable=True)
    net_other_financing_charges: Mapped[float] = mapped_column(nullable=True)
    cash_dividends_paid: Mapped[float] = mapped_column(nullable=True)
    net_common_stock_issuance: Mapped[float] = mapped_column(nullable=True)
    common_stock_payments: Mapped[float] = mapped_column(nullable=True)
    net_issuance_payments_of_debt: Mapped[float] = mapped_column(nullable=True)
    net_long_term_debt_issuance: Mapped[float] = mapped_column(nullable=True)
    long_term_debt_payments: Mapped[float] = mapped_column(nullable=True)
    long_term_debt_issuance: Mapped[float] = mapped_column(nullable=True)
    investing_cash_flow: Mapped[float] = mapped_column(nullable=True)
    net_other_investing_changes: Mapped[float] = mapped_column(nullable=True)
    dividends_received_cfi: Mapped[float] = mapped_column(nullable=True)
    net_investment_purchase_and_sale: Mapped[float] = mapped_column(nullable=True)
    sale_of_investment: Mapped[float] = mapped_column(nullable=True)
    purchase_of_investment: Mapped[float] = mapped_column(nullable=True)
    net_business_purchase_and_sale: Mapped[float] = mapped_column(nullable=True)
    sale_of_business: Mapped[float] = mapped_column(nullable=True)
    purchase_of_business: Mapped[float] = mapped_column(nullable=True)
    net_intangibles_purchase_and_sale: Mapped[float] = mapped_column(nullable=True)
    sale_of_intangibles: Mapped[float] = mapped_column(nullable=True)
    purchase_of_intangibles: Mapped[float] = mapped_column(nullable=True)
    net_ppe_purchase_and_sale: Mapped[float] = mapped_column(nullable=True)
    sale_of_ppe: Mapped[float] = mapped_column(nullable=True)
    purchase_of_ppe: Mapped[float] = mapped_column(nullable=True)
    operating_cash_flow: Mapped[float] = mapped_column(nullable=True)
    taxes_refund_paid: Mapped[float] = mapped_column(nullable=True)
    interest_received_cfo: Mapped[float] = mapped_column(nullable=True)
    interest_paid_cfo: Mapped[float] = mapped_column(nullable=True)
    change_in_working_capital: Mapped[float] = mapped_column(nullable=True)
    change_in_other_current_assets: Mapped[float] = mapped_column(nullable=True)
    other_non_cash_items: Mapped[float] = mapped_column(nullable=True)
    stock_based_compensation: Mapped[float] = mapped_column(nullable=True)
    provisionand_write_offof_assets: Mapped[float] = mapped_column(nullable=True)
    deferred_tax: Mapped[float] = mapped_column(nullable=True)
    depreciation_and_amortization: Mapped[float] = mapped_column(nullable=True)
    amortization_cash_flow: Mapped[float] = mapped_column(nullable=True)
    depreciation: Mapped[float] = mapped_column(nullable=True)
    net_foreign_currency_exchange_gain_loss: Mapped[float] = mapped_column(nullable=True)
    gain_loss_on_sale_of_ppe: Mapped[float] = mapped_column(nullable=True)
    net_income_from_continuing_operations: Mapped[float] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
