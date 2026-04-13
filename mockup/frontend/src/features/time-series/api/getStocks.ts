import { apiGet } from "../../../lib/api/client";
import type { StocksResponse } from "../types/stocks";

export function getStocks() {
  return apiGet<StocksResponse>(`/api/v1/stocks/`);
}