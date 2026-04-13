import { afterEach, describe, expect, it, vi } from "vitest";

import { getStocks } from "../features/time-series/api/getStocks";
import { apiGet } from "../lib/api/client";
import type { StocksResponse } from "../features/time-series/types/stocks";

vi.mock("../lib/api/client", () => ({
  apiGet: vi.fn(),
}));

describe("getStocks", () => {
  afterEach(() => {
    vi.clearAllMocks();
  });

  it("calls /api/v1/stocks/ and returns response", async () => {
    const response: StocksResponse = {
      results: [
        {
          id: 1,
          code: "7203",
          market: "TSE",
          name: null,
          sector: null,
          memo: null,
          created_at: "2026-04-12T01:38:35.677888Z",
          updated_at: "2026-04-12T01:38:35.677888Z",
        },
      ],
    };

    const mockedApiGet = vi.mocked(apiGet);
    mockedApiGet.mockResolvedValue(response);

    const result = await getStocks();

    expect(mockedApiGet).toHaveBeenCalledTimes(1);
    expect(mockedApiGet).toHaveBeenCalledWith("/api/v1/stocks/");
    expect(result).toEqual(response);
  });
});
