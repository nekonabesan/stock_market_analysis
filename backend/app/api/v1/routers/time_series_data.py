from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.time_series_data import TimeSeriesDataGetRequest, TimeSeriesDataGetResponse
from app.api.v1.services.time_series_data import TimeSeriesDataService

router = APIRouter()

@router.get(
    "",
    response_model=TimeSeriesDataGetResponse,
    status_code=status.HTTP_200_OK,
    summary="銘柄コードの株価データを取得",
    description="指定した銘柄コードの株価データをDBから取得する。",
)
def get_time_series_data(
    request: TimeSeriesDataGetRequest = Depends(),
    db: Session = Depends(get_db),
) -> TimeSeriesDataGetResponse:
    try:
        service = TimeSeriesDataService(db)
        data = service.get_time_series_data(
            code=request.code,
            market=request.market,
            start=request.start,
            end=request.end,
        )
        if not data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Stock data not found",
            )

        return TimeSeriesDataGetResponse(
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