import { describe, expect, it, vi } from "vitest";

import { upsertStockPrice } from "../features/stocks/api/upsertStockPrice";
import { apiPost } from "../lib/api/client";

vi.mock("../lib/api/client", () => ({
  apiPost: vi.fn(),
}));

describe("upsertStockPrice", () => {
  it("calls /api/v1/stock_price/ with payload", async () => {
    const mockedApiPost = vi.mocked(apiPost);
    mockedApiPost.mockResolvedValue({ result: true });

    await upsertStockPrice({
      code: "7203.T",
      market: "TSE",
      start: "2026-04-01",
      end: "2026-04-30",
      name: "トヨタ自動車",
    });

    expect(mockedApiPost).toHaveBeenCalledTimes(1);
    expect(mockedApiPost).toHaveBeenCalledWith("/api/v1/stock_price/", {
      code: "7203.T",
      market: "TSE",
      start: "2026-04-01",
      end: "2026-04-30",
      name: "トヨタ自動車",
    });
  });
});
