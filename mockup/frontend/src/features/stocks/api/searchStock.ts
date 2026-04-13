import { apiPost } from "../../../lib/api/client";
import type { SearchRequest, SearchResponse } from "../types/search";

export function searchStock(payload: SearchRequest) {
  return apiPost<SearchResponse>("/api/v1/search/", payload);
}
