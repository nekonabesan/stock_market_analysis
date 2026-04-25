from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import inspect as sa_inspect
from sqlalchemy.orm import Session

import math
import numpy as np

from app.db.session import get_db
from app.schemas.corp_finance_data import (
    BalanceSheetGetRequest,
    BalanceSheetGetResponse,
    CashFlowGetRequest,
    CashFlowGetResponse,
    CorporateFinanceDataUpdateRequest,
    CorporateFinanceDataUpdateResponse,
    EarningsGetRequest,
    EarningsGetResponse,
    FinanceDataGetRequest,
    FinanceDataGetResponse,
    QuarterlyEarningsGetRequest,
    QuarterlyEarningsGetResponse,
)
from app.api.v1.services.corp_finance_data import CorporateFinanceDataService
from app.api.v1.services.orm_serializer import OrmSerializer

router = APIRouter()


# Use OrmSerializer.to_dict in handlers; keep router thin (no business logic)


@router.post(
    "/",
    response_model=CorporateFinanceDataUpdateResponse,
    status_code=status.HTTP_200_OK,
    summary="財務データをUPSERT",
    description="財務データをDBにUPDATE/INSERTする。",
)
def upsert_stock_data(
    request: CorporateFinanceDataUpdateRequest,
    db: Session = Depends(get_db),
) -> CorporateFinanceDataUpdateResponse:
    try:
        service = CorporateFinanceDataService(db_session=db)
        success = service.update_corp_finance_data(
            code=request.code,
            market=request.market,
        )
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Corporate finance data not found or could not be fetched",
            )

        return CorporateFinanceDataUpdateResponse(
            result=success,
        )
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        ) from e


@router.get(
    "/financials/",
    response_model=FinanceDataGetResponse,
    status_code=status.HTTP_200_OK,
    summary="財務諸表データを取得",
    description="指定した銘柄コードの財務諸表データをDBから取得する。",
)
def get_financials(
    request: FinanceDataGetRequest = Depends(),
    db: Session = Depends(get_db),
) -> FinanceDataGetResponse:
    try:
        service = CorporateFinanceDataService(db_session=db)
        data = service.get_financial_statements(
            code=request.code,
            market=request.market,
            start=request.start,
            end=request.end,
        )
        if not data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Corporate finance data not found",
            )

        return FinanceDataGetResponse(
            results=[OrmSerializer.to_dict(r) for r in data],
        )
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        ) from e


@router.get(
    "/balance_sheet/",
    response_model=BalanceSheetGetResponse,
    status_code=status.HTTP_200_OK,
    summary="バランスシートデータを取得",
    description="指定した銘柄コードのバランスシートデータをDBから取得する。",
)
def get_balance_sheet(
    request: BalanceSheetGetRequest = Depends(),
    db: Session = Depends(get_db),
) -> BalanceSheetGetResponse:
    try:
        service = CorporateFinanceDataService(db_session=db)
        data = service.get_balance_sheet(
            code=request.code,
            market=request.market,
            start=request.start,
            end=request.end,
        )
        if not data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Balance sheet data not found",
            )

        return BalanceSheetGetResponse(
            results=[OrmSerializer.to_dict(r) for r in data],
        )
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        ) from e


@router.get(
    "/cash_flow/",
    response_model=CashFlowGetResponse,
    status_code=status.HTTP_200_OK,
    summary="キャッシュフローデータを取得",
    description="指定した銘柄コードのキャッシュフローデータをDBから取得する。",
)
def get_cash_flow(
    request: CashFlowGetRequest = Depends(),
    db: Session = Depends(get_db),
) -> CashFlowGetResponse:
    try:
        service = CorporateFinanceDataService(db_session=db)
        data = service.get_cashflow(
            code=request.code,
            market=request.market,
            start=request.start,
            end=request.end,
        )
        if not data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cash flow data not found",
            )

        return CashFlowGetResponse(
            results=[OrmSerializer.to_dict(r) for r in data],
        )
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        ) from e


@router.get(
    "/earnings/",
    response_model=EarningsGetResponse,
    status_code=status.HTTP_200_OK,
    summary="損益計算書データを取得",
    description="指定した銘柄コードの損益計算書データをDBから取得する。",
)
def get_earnings(
    request: EarningsGetRequest = Depends(),
    db: Session = Depends(get_db),
) -> EarningsGetResponse:
    try:
        service = CorporateFinanceDataService(db_session=db)
        data = service.get_earnings(
            code=request.code,
            market=request.market,
            start=request.start,
            end=request.end,
        )
        if not data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Earnings data not found",
            )

        return EarningsGetResponse(
            results=[OrmSerializer.to_dict(r) for r in data],
        )
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        ) from e


@router.get(
    "/quarterly_earnings/",
    response_model=QuarterlyEarningsGetResponse,
    status_code=status.HTTP_200_OK,
    summary="四半期損益計算書データを取得",
    description="指定した銘柄コードの四半期損益計算書データをDBから取得する。",
)
def get_quarterly_earnings(
    request: QuarterlyEarningsGetRequest = Depends(),
    db: Session = Depends(get_db),
) -> QuarterlyEarningsGetResponse:
    try:
        service = CorporateFinanceDataService(db_session=db)
        data = service.get_quarterly_earnings(
            code=request.code,
            market=request.market,
            start=request.start,
            end=request.end,
        )
        if not data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Quarterly earnings data not found",
            )

        return QuarterlyEarningsGetResponse(
            results=[OrmSerializer.to_dict(r) for r in data],
        )
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        ) from e
