from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.commodity_data import (
    CommodityDataUpsertRequest,
    CommodityDataUpsertResponse,
    CommodityDataGetRequest,
    CommodityDataGetResponse
)
from app.api.v1.services.commodity_data import CommodityDataService

router = APIRouter()

@router.post(
    "/",
    response_model=CommodityDataUpsertResponse,
    status_code=status.HTTP_200_OK,
    summary="銘柄コードの株価データをUPSERT",
    description="指定した銘柄コードの株価データを取得し、DBにUPDATE/INSERTする。",
)
def upsert_commodity_data(
    request: CommodityDataUpsertRequest,
    db: Session = Depends(get_db),
) -> CommodityDataUpsertResponse:
    try:
        service = CommodityDataService(db)
        success = service.update_commodity_data(
            code=request.code,
            market=request.market,
            start=request.start,
            end=request.end,
        )
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Commodity data not found or could not be fetched",
            )

        return CommodityDataUpsertResponse(
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
    response_model=CommodityDataGetResponse,
    status_code=status.HTTP_200_OK,
    summary="銘柄コードの株価データを取得",
    description="指定した銘柄コードの株価データをDBから取得する。",
)
def get_commodity_data(
    request: CommodityDataGetRequest = Depends(),
    db: Session = Depends(get_db),
) -> CommodityDataGetResponse:
    try:
        service = CommodityDataService(db)
        data = service.get_commodity_data(
            code=request.code,
            market=request.market,
            start=request.start,
            end=request.end,
        )
        if data is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Commodity data not found",
            )

        return CommodityDataGetResponse(
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
