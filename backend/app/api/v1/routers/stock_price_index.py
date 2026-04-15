from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.stock_price_index import StockPriceUpsertRequest, StockPriceUpsertResponse, StockPriceIndexGetRequest, StockPriceIndexGetResponse
from app.api.v1.services.stock_price_index import StockPriceIndexService

router = APIRouter()


@router.post(
    "/all/",
    response_model=StockPriceUpsertResponse,
    status_code=status.HTTP_200_OK,
    summary="全ての株価インデクスデータをUPSERT",
    description="全ての株価インデクスデータをDBにUPDATE/INSERTする。",
)
def upsert_all_stock_data(
    request: StockPriceUpsertRequest,
    db: Session = Depends(get_db),
) -> StockPriceUpsertResponse:
    try:
        service = StockPriceIndexService(db)
        success = service.update_all_index_data(
            start=request.start,
            end=request.end,
        )
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Stock price index data not found or could not be fetched",
            )

        return StockPriceUpsertResponse(
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

@router.post(
    "/",
    response_model=StockPriceUpsertResponse,
    status_code=status.HTTP_200_OK,
    summary="株価インデクスデータをUPSERT",
    description="株価インデクスデータをDBにUPDATE/INSERTする。",
)
def upsert_stock_data(
    request: StockPriceUpsertRequest,
    db: Session = Depends(get_db),
) -> StockPriceUpsertResponse:
    try:
        service = StockPriceIndexService(db)
        success = service.update_index_data(
            code=request.code,
            market=request.market,
            start=request.start,
            end=request.end,
        )
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Stock price index data not found or could not be fetched",
            )

        return StockPriceUpsertResponse(
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
    "/",
    response_model=StockPriceIndexGetResponse,
    status_code=status.HTTP_200_OK,
    summary="株価インデクスデータを取得",
    description="指定したコードの株価インデクスデータをDBから取得する。",
)
def get_index_data(
    request: StockPriceIndexGetRequest = Depends(),
    db: Session = Depends(get_db),
) -> StockPriceIndexGetResponse:
    try:
        service = StockPriceIndexService(db)
        data = service.get_index_data(
            code=request.code,
            market=request.market,
            start=request.start,
            end=request.end,
        )
        if data is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Stock price index data not found",
            )

        return StockPriceIndexGetResponse(
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
