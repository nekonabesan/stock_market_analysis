import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { MarketSelector } from "../features/stocks/components/MarketSelector";
import { Stock } from "../features/stocks/types/stock";

const mockStocks: Stock[] = [
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

describe("MarketSelector", () => {
  it("should render with market label", () => {
    const mockOnChange = vi.fn();
    render(
      <MarketSelector stocks={mockStocks} value="" onChange={mockOnChange} />
    );

    const label = screen.getByText("市場");
    expect(label).toBeInTheDocument();
  });

  it("should display market options extracted from stocks", () => {
    const mockOnChange = vi.fn();
    render(
      <MarketSelector stocks={mockStocks} value="" onChange={mockOnChange} />
    );

    const marketSelect = screen.getByLabelText("市場") as HTMLSelectElement;
    const options = Array.from(marketSelect.options).map((o) => o.value);

    expect(options).toContain("");
    expect(options).toContain("JPX");
    expect(options).toContain("TSE");
  });

  it("should call onChange when market is changed", () => {
    const mockOnChange = vi.fn();
    render(
      <MarketSelector stocks={mockStocks} value="" onChange={mockOnChange} />
    );

    const marketSelect = screen.getByLabelText("市場") as HTMLSelectElement;
    fireEvent.change(marketSelect, { target: { value: "TSE" } });

    expect(mockOnChange).toHaveBeenCalledWith("TSE");
    expect(mockOnChange).toHaveBeenCalledTimes(1);
  });

  it("should display selected market value", () => {
    const mockOnChange = vi.fn();
    const { rerender } = render(
      <MarketSelector stocks={mockStocks} value="" onChange={mockOnChange} />
    );

    let marketSelect = screen.getByLabelText("市場") as HTMLSelectElement;
    expect(marketSelect).toHaveValue("");

    rerender(
      <MarketSelector stocks={mockStocks} value="TSE" onChange={mockOnChange} />
    );

    marketSelect = screen.getByLabelText("市場") as HTMLSelectElement;
    expect(marketSelect).toHaveValue("TSE");
  });

  it("should remove duplicate market values", () => {
    const mockOnChange = vi.fn();
    const stocksWithDuplicates: Stock[] = [
      ...mockStocks,
      {
        id: 4,
        code: "1234.T",
        market: "TSE",
        name: "テスト銘柄",
        sector: "テスト",
        memo: null,
        created_at: "2024-01-01T00:00:00Z",
        updated_at: "2024-01-01T00:00:00Z",
      },
    ];

    render(
      <MarketSelector
        stocks={stocksWithDuplicates}
        value=""
        onChange={mockOnChange}
      />
    );

    const marketSelect = screen.getByLabelText("市場") as HTMLSelectElement;
    const options = Array.from(marketSelect.options)
      .map((o) => o.value)
      .filter((v) => v !== "");

    // TSEはユニークに1つだけ
    const tseCount = options.filter((v) => v === "TSE").length;
    expect(tseCount).toBe(1);
  });
});
