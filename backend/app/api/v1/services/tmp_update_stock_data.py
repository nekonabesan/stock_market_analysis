import datetime as dt
from app.api.v1.services.stock_data import StockDataService
from app.db.session import SessionLocal

if __name__ == "__main__":
    code = "7270"
    market = "TSE"
    start = dt.date(1999, 1, 1)
    end = dt.date(2024, 12, 31)

    with SessionLocal() as session:
        service = StockDataService(session)
        try:
            result = service.update_stock_data(code=code, market=market, start=start, end=end)
            print(f"update_stock_data result: {result}")
            rows = session.execute(
                "SELECT COUNT(*) FROM trn_stock_price WHERE stock_code = :code AND stock_market = :market",
                {"code": code, "market": market}
            ).scalar()
            print(f"trn_stock_price rows for {code}, {market}: {rows}")
        except Exception as e:
            print(f"Error: {e}")
