from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.stocks import StockGetRequest, StockGetResponse
from app.api.v1.services.stocks import StocksService

router = APIRouter()

@router.get(
    "/",
    response_model=StockGetResponse,
    status_code=status.HTTP_200_OK,
    summary="銘柄の基本情報を取得",
    description="指定した銘柄の基本情報を取得する。",
)
def get_stocks(
    request: StockGetRequest = Depends(),
    db: Session = Depends(get_db),
) -> StockGetResponse:
    try:
        service = StocksService(db)
        stocks = service.get_stock_data()
        if stocks is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Stock data not found",
            )

        return StockGetResponse(
            results=stocks,
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
