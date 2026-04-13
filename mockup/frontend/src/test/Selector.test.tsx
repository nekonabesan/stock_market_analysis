import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { fireEvent, render, screen } from "@testing-library/react";
import { Selector } from "../features/stocks/components/Selector";
import * as useStocksModule from "../features/stocks/hooks/useStocks";

vi.mock("../features/stocks/hooks/useStocks");

const mockStocks = [
  {
    id: 1,
    code: "7203.T",
    market: "TSE",
    name: "トヨタ自動車",
    sector: "自動車",
    memo: null,
    created_at: "2024-01-01T00:00:00Z",
    updated_at: "2024-01-01T00:00:00Z",
  },
  {
    id: 2,
    code: "6758.T",
    market: "TSE",
    name: "ソニーグループ",
    sector: "電子機器",
    memo: null,
    created_at: "2024-01-01T00:00:00Z",
    updated_at: "2024-01-01T00:00:00Z",
  },
  {
    id: 3,
    code: "9984.T",
    market: "JPX",
    name: "ソフトバンクグループ",
    sector: "情報通信",
    memo: null,
    created_at: "2024-01-01T00:00:00Z",
    updated_at: "2024-01-01T00:00:00Z",
  },
];

describe("Selector", () => {
  beforeEach(() => {
    vi.useFakeTimers();
    vi.setSystemTime(new Date("2026-04-13T10:00:00Z"));
    const mockUseStocks = vi.fn(() => ({
      stocks: mockStocks,
      isLoading: false,
      error: null,
    }));
    vi.mocked(useStocksModule.useStocks).mockImplementation(mockUseStocks);
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it("should render selector with all form controls", () => {
    render(<Selector onChange={vi.fn()} />);

    expect(screen.getByText("データセレクタ")).toBeInTheDocument();
    expect(screen.getByLabelText("市場")).toBeInTheDocument();
    expect(screen.getByLabelText("銘柄")).toBeInTheDocument();
    expect(screen.getByLabelText("データ取得開始期間")).toBeInTheDocument();
    expect(screen.getByLabelText("データ取得終了期間")).toBeInTheDocument();
  });

  it("should display market options", () => {
    render(<Selector onChange={vi.fn()} />);

    const marketSelect = screen.getByLabelText("市場") as HTMLSelectElement;
    const options = Array.from(marketSelect.options).map((o) => o.value);

    expect(options).toContain("");
    expect(options).toContain("JPX");
    expect(options).toContain("TSE");
  });

  it("should render StockSelector component", () => {
    render(<Selector onChange={vi.fn()} />);

    expect(screen.getByLabelText("銘柄")).toBeInTheDocument();
  });

  it("should initialize start and end date with current month range", () => {
    render(<Selector onChange={vi.fn()} />);

    const startInput = screen.getByLabelText("データ取得開始期間") as HTMLInputElement;
    const endInput = screen.getByLabelText("データ取得終了期間") as HTMLInputElement;

    expect(startInput.value).toBe("2026-04-01");
    expect(endInput.value).toBe("2026-04-30");
  });

  it("should call onChange when selector values are changed", () => {
    const onChange = vi.fn();
    render(<Selector onChange={onChange} />);

    const marketSelect = screen.getByLabelText("市場");
    const stockSelect = screen.getByLabelText("銘柄");
    const startInput = screen.getByLabelText("データ取得開始期間");

    fireEvent.change(marketSelect, { target: { value: "TSE" } });
    fireEvent.change(stockSelect, { target: { value: "7203.T" } });
    fireEvent.change(startInput, { target: { value: "2026-04-05" } });

    expect(onChange).toHaveBeenCalled();
    expect(onChange).toHaveBeenLastCalledWith({
      market: "TSE",
      code: "7203.T",
      start: "2026-04-05",
      end: "2026-04-30",
    });
  });

  it("should display loading state", () => {
    const mockUseStocks = vi.fn(() => ({
      stocks: [],
      isLoading: true,
      error: null,
    }));
    vi.mocked(useStocksModule.useStocks).mockImplementation(mockUseStocks);

    render(<Selector onChange={vi.fn()} />);

    expect(screen.getByText("Loading...")).toBeInTheDocument();
  });

  it("should display error state", () => {
    const mockUseStocks = vi.fn(() => ({
      stocks: [],
      isLoading: false,
      error: "Failed to fetch stocks",
    }));
    vi.mocked(useStocksModule.useStocks).mockImplementation(mockUseStocks);

    render(<Selector onChange={vi.fn()} />);

    expect(screen.getByText("Failed to fetch stocks")).toBeInTheDocument();
  });
});
