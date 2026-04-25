from datetime import date as dt_date, datetime

from sqlalchemy import Date, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class Financials(Base):
    __tablename__ = "trn_financials"

    date: Mapped[dt_date] = mapped_column(Date, primary_key=True, nullable=False)
    market: Mapped[str | None] = mapped_column(String(64), nullable=True)
    code: Mapped[str] = mapped_column(String(16), primary_key=True, nullable=False)
    tax_effect_of_unusual_items: Mapped[float] = mapped_column(nullable=True)
    tax_rate_for_calcs: Mapped[float] = mapped_column(nullable=True)
    normalized_ebitda: Mapped[float] = mapped_column(nullable=True)
    total_unusual_items: Mapped[float] = mapped_column(nullable=True)
    total_unusual_items_excluding_goodwill: Mapped[float] = mapped_column(nullable=True)
    net_income_from_continuing_operation_net_minority_interest: Mapped[float] = mapped_column(nullable=True)
    reconciled_depreciation: Mapped[float] = mapped_column(nullable=True)
    reconciled_cost_of_revenue: Mapped[float] = mapped_column(nullable=True)
    ebitda: Mapped[float] = mapped_column(nullable=True)
    ebit: Mapped[float] = mapped_column(nullable=True)
    net_interest_income: Mapped[float] = mapped_column(nullable=True)
    interest_expense: Mapped[float] = mapped_column(nullable=True)
    interest_income: Mapped[float] = mapped_column(nullable=True)
    normalized_income: Mapped[float] = mapped_column(nullable=True)
    net_income_from_continuing_and_discontinued_operation: Mapped[float] = mapped_column(nullable=True)
    total_expenses: Mapped[float] = mapped_column(nullable=True)
    total_operating_income_as_reported: Mapped[float] = mapped_column(nullable=True)
    diluted_average_shares: Mapped[float] = mapped_column(nullable=True)
    basic_average_shares: Mapped[float] = mapped_column(nullable=True)
    diluted_eps: Mapped[float] = mapped_column(nullable=True)
    basic_eps: Mapped[float] = mapped_column(nullable=True)
    diluted_ni_availto_com_stockholders: Mapped[float] = mapped_column(nullable=True)
    net_income_common_stockholders: Mapped[float] = mapped_column(nullable=True)
    otherunder_preferred_stock_dividend: Mapped[float] = mapped_column(nullable=True)
    net_income: Mapped[float] = mapped_column(nullable=True)
    minority_interests: Mapped[float] = mapped_column(nullable=True)
    net_income_including_noncontrolling_interests: Mapped[float] = mapped_column(nullable=True)
    net_income_continuous_operations: Mapped[float] = mapped_column(nullable=True)
    tax_provision: Mapped[float] = mapped_column(nullable=True)
    pretax_income: Mapped[float] = mapped_column(nullable=True)
    special_income_charges: Mapped[float] = mapped_column(nullable=True)
    other_special_charges: Mapped[float] = mapped_column(nullable=True)
    write_off: Mapped[float] = mapped_column(nullable=True)
    impairment_of_capital_assets: Mapped[float] = mapped_column(nullable=True)
    net_non_operating_interest_income_expense: Mapped[float] = mapped_column(nullable=True)
    total_other_finance_cost: Mapped[float] = mapped_column(nullable=True)
    interest_expense_non_operating: Mapped[float] = mapped_column(nullable=True)
    interest_income_non_operating: Mapped[float] = mapped_column(nullable=True)
    operating_income: Mapped[float] = mapped_column(nullable=True)
    operating_expense: Mapped[float] = mapped_column(nullable=True)
    other_operating_expenses: Mapped[float] = mapped_column(nullable=True)
    research_and_development: Mapped[float] = mapped_column(nullable=True)
    selling_general_and_administration: Mapped[float] = mapped_column(nullable=True)
    selling_and_marketing_expense: Mapped[float] = mapped_column(nullable=True)
    general_and_administrative_expense: Mapped[float] = mapped_column(nullable=True)
    gross_profit: Mapped[float] = mapped_column(nullable=True)
    cost_of_revenue: Mapped[float] = mapped_column(nullable=True)
    total_revenue: Mapped[float] = mapped_column(nullable=True)
    operating_revenue: Mapped[float] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    
