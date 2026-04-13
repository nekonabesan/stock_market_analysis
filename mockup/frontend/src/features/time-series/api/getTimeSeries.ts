import { apiGet } from "../../../lib/api/client";
import type { TimeSeriesResponse } from "../types/timeSeries";

type Params = {
  code: string;
  market?: string;
  start: string;
  end: string;
};

export function getTimeSeries(params: Params) {
  const search = new URLSearchParams({
    code: params.code,
    market: params.market ?? "TSE",
    start: params.start,
    end: params.end,
  });

  return apiGet<TimeSeriesResponse>(`/api/v1/time_series_data?${search.toString()}`);
}