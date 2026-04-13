import { describe, expect, it } from "vitest";

import type { Stock, StocksResponse } from "../features/time-series/types/stocks";

describe("stocks types", () => {
  it("accepts endpoint response shape", () => {
    const stock: Stock = {
      id: 1,
      code: "7203",
      market: "TSE",
      name: null,
      sector: null,
      memo: null,
      created_at: "2026-04-12T01:38:35.677888Z",
      updated_at: "2026-04-12T01:38:35.677888Z",
    };

    const response: StocksResponse = {
      results: [stock],
    };

    expect(response.results[0].code).toBe("7203");
    expect(response.results[0].id).toBe(1);
  });

  it("supports null fields from database", () => {
    const stock: Stock = {
      id: 2,
      code: "6758",
      market: "TSE",
      name: null,
      sector: null,
      memo: null,
      created_at: "2026-04-12T01:38:37.050763Z",
      updated_at: "2026-04-12T01:38:37.050763Z",
    };

    expect(stock.name).toBeNull();
    expect(stock.sector).toBeNull();
    expect(stock.memo).toBeNull();
  });
});
