from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.stock_data import StockDataUpsertRequest, StockDataUpsertResponse, StockDataGetRequest, StockDataGetResponse
from app.api.v1.services.stock_data import StockDataService

router = APIRouter()


@router.post(
    "/data",
    response_model=StockDataUpsertResponse,
    status_code=status.HTTP_200_OK,
    summary="銘柄コードの株価データをUPSERT",
    description="指定した銘柄コードの株価データを取得し、DBにUPDATE/INSERTする。",
)
def upsert_stock_data(
    request: StockDataUpsertRequest,
    db: Session = Depends(get_db),
) -> StockDataUpsertResponse:
    try:
        service = StockDataService(db)
        success = service.update_stock_data(
            code=request.code,
            market=request.market,
            start=request.start,
            end=request.end,
        )
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Stock data not found or could not be fetched",
            )

        return StockDataUpsertResponse(
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
    "/get",
    response_model=StockDataGetResponse,
    status_code=status.HTTP_200_OK,
    summary="銘柄コードの株価データを取得",
    description="指定した銘柄コードの株価データをDBから取得する。",
)
def get_stock_data(
    request: StockDataGetRequest = Depends(),
    db: Session = Depends(get_db),
) -> StockDataGetResponse:
    try:
        service = StockDataService(db)
        data = service.get_stock_data(
            code=request.code,
            market=request.market,
            start=request.start,
            end=request.end,
        )
        if data is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Stock data not found",
            )

        return StockDataGetResponse(
            results=data,
        )
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        ) from e
