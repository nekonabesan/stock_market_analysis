import { apiPost } from "../../../lib/api/client";
import type {
  UpsertStockPriceRequest,
  UpsertStockPriceResponse,
} from "../types/stockPrice";

export function upsertStockPrice(payload: UpsertStockPriceRequest) {
  return apiPost<UpsertStockPriceResponse>("/api/v1/stock_price/", payload);
}
