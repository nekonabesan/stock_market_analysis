import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";

import { TimeSeries } from "../features/time-series/components/TimeSeries";
import * as useTimeSeriesModule from "../features/time-series/hooks/useTimeSeries";

vi.mock("../features/time-series/hooks/useTimeSeries");

const baseCriteria = {
  market: "TSE",
  code: "7203.T",
  start: "2026-04-01",
  end: "2026-04-30",
};

describe("TimeSeries", () => {
  beforeEach(() => {
    vi.mocked(useTimeSeriesModule.useTimeSeries).mockReturnValue({
      rows: [],
      isLoading: false,
      error: null,
    });
  });

  it("shows placeholder when code is empty", () => {
    render(
      <TimeSeries
        criteria={{ market: "", code: "", start: "2026-04-01", end: "2026-04-30" }}
      />
    );

    expect(screen.getByText("銘柄を選択するとグラフを表示します。")).toBeInTheDocument();
  });

  it("shows loading while fetching", () => {
    vi.mocked(useTimeSeriesModule.useTimeSeries).mockReturnValue({
      rows: [],
      isLoading: true,
      error: null,
    });

    render(<TimeSeries criteria={baseCriteria} />);

    expect(screen.getByText("Loading...")).toBeInTheDocument();
  });

  it("shows error when request fails", () => {
    vi.mocked(useTimeSeriesModule.useTimeSeries).mockReturnValue({
      rows: [],
      isLoading: false,
      error: "Failed to fetch",
    });

    render(<TimeSeries criteria={baseCriteria} />);

    expect(screen.getByText("Failed to fetch")).toBeInTheDocument();
  });

  it("shows chart when request succeeds", () => {
    vi.mocked(useTimeSeriesModule.useTimeSeries).mockReturnValue({
      rows: [
        {
          date: "2026-03-31",
          open: 98,
          high: 108,
          low: 88,
          close: 100,
          volume: 8000,
          upper2: 112,
          lower2: 84,
        },
        {
          date: "2026-04-01",
          open: 100,
          high: 110,
          low: 90,
          close: 105,
          volume: 10000,
          upper2: 114,
          lower2: 86,
        },
      ],
      isLoading: false,
      error: null,
    });

    render(<TimeSeries criteria={baseCriteria} />);

    expect(screen.getByRole("img", { name: "時系列チャート" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "7203.T" })).toBeInTheDocument();
    expect(screen.getByTestId("bb-band")).toBeInTheDocument();
  });
});
