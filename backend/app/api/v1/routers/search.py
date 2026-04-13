from fastapi import APIRouter, HTTPException, status

from app.api.v1.services.search import SearchService
from app.schemas.search import SearchRequest, SearchResponse

router = APIRouter()


@router.post(
    "/",
    response_model=SearchResponse,
    status_code=status.HTTP_200_OK,
    summary="Yahoo Financeで銘柄検索",
    description="市場と銘柄名または銘柄コードを使ってYahoo Financeで銘柄の取得可否を確認する。",
)
def search_stocks(request: SearchRequest) -> SearchResponse:
    try:
        service = SearchService()
        result = service.search(
            market=request.market,
            name=request.name,
            code=request.code,
        )
        if result is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Stock data not found",
            )

        return SearchResponse(**result)
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
