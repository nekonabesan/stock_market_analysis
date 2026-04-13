import { describe, it, expect, vi } from "vitest";

import { getTimeSeries } from "../features/time-series/api/getTimeSeries";
import { apiGet } from "../lib/api/client";

vi.mock("../lib/api/client", () => ({
  apiGet: vi.fn(),
}));

describe("getTimeSeries", () => {
  it("calls /api/v1/time_series_data with query params", async () => {
    const mockedApiGet = vi.mocked(apiGet);
    mockedApiGet.mockResolvedValue({ results: [] });

    await getTimeSeries({
      code: "7203.T",
      market: "TSE",
      start: "2026-04-01",
      end: "2026-04-30",
    });

    expect(mockedApiGet).toHaveBeenCalledTimes(1);
    expect(mockedApiGet).toHaveBeenCalledWith(
      "/api/v1/time_series_data?code=7203.T&market=TSE&start=2026-04-01&end=2026-04-30"
    );
  });
});
