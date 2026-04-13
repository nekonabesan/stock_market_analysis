import { describe, expect, it, vi } from "vitest";

import { searchStock } from "../features/stocks/api/searchStock";
import { apiPost } from "../lib/api/client";

vi.mock("../lib/api/client", () => ({
  apiPost: vi.fn(),
}));

describe("searchStock", () => {
  it("calls /api/v1/search/ with payload", async () => {
    const mockedApiPost = vi.mocked(apiPost);
    mockedApiPost.mockResolvedValue({
      found: true,
      market: "TSE",
      name: "TOYOTA",
      code: "7203.T",
    });

    await searchStock({ market: "TSE", code: "7203" });

    expect(mockedApiPost).toHaveBeenCalledTimes(1);
    expect(mockedApiPost).toHaveBeenCalledWith("/api/v1/search/", {
      market: "TSE",
      code: "7203",
    });
  });
});
