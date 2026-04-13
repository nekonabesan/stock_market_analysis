import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { StockSelector } from "../features/stocks/components/StockSelector";
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

describe("StockSelector", () => {
  it("should render with stock label", () => {
    const mockOnChange = vi.fn();
    render(
      <StockSelector stocks={mockStocks} value="" onChange={mockOnChange} />
    );

    expect(screen.getByLabelText("銘柄")).toBeInTheDocument();
  });

  it("should display all stock options", () => {
    const mockOnChange = vi.fn();
    render(
      <StockSelector stocks={mockStocks} value="" onChange={mockOnChange} />
    );

    expect(screen.getByText("トヨタ自動車 (7203.T)")).toBeInTheDocument();
    expect(screen.getByText("ソニーグループ (6758.T)")).toBeInTheDocument();
    expect(screen.getByText("ソフトバンクグループ (9984.T)")).toBeInTheDocument();
  });

  it("should call onChange when stock is changed", () => {
    const mockOnChange = vi.fn();
    render(
      <StockSelector stocks={mockStocks} value="" onChange={mockOnChange} />
    );

    const select = screen.getByRole("combobox");
    fireEvent.change(select, { target: { value: "7203.T" } });

    expect(mockOnChange).toHaveBeenCalledWith("7203.T");
    expect(mockOnChange).toHaveBeenCalledTimes(1);
  });

  it("should display selected stock value", () => {
    const mockOnChange = vi.fn();
    const { rerender } = render(
      <StockSelector stocks={mockStocks} value="" onChange={mockOnChange} />
    );

    let select = screen.getByRole("combobox") as HTMLSelectElement;
    expect(select).toHaveValue("");

    rerender(
      <StockSelector
        stocks={mockStocks}
        value="7203.T"
        onChange={mockOnChange}
      />
    );

    select = screen.getByRole("combobox") as HTMLSelectElement;
    expect(select).toHaveValue("7203.T");
  });

  it("should display placeholder text for empty selection", () => {
    const mockOnChange = vi.fn();
    render(
      <StockSelector stocks={mockStocks} value="" onChange={mockOnChange} />
    );

    expect(
      screen.getByText("銘柄を選択してください")
    ).toBeInTheDocument();
  });

  it("should handle stocks with null names", () => {
    const stocksWithNullName: Stock[] = [
      {
        id: 1,
        code: "0000.T",
        market: "TSE",
        name: null,
        sector: null,
        memo: null,
        created_at: "2024-01-01T00:00:00Z",
        updated_at: "2024-01-01T00:00:00Z",
      },
    ];

    const mockOnChange = vi.fn();
    render(
      <StockSelector
        stocks={stocksWithNullName}
        value=""
        onChange={mockOnChange}
      />
    );

    expect(screen.getByText("銘柄名なし (0000.T)")).toBeInTheDocument();
  });

  it("should limit display to first 200 stocks", () => {
    const manyStocks = Array.from({ length: 300 }, (_, i) => ({
      id: i,
      code: `${String(i).padStart(4, "0")}.T`,
      market: "TSE",
      name: `Stock ${i}`,
      sector: "test",
      memo: null,
      created_at: "2024-01-01T00:00:00Z",
      updated_at: "2024-01-01T00:00:00Z",
    }));

    const mockOnChange = vi.fn();
    const { container } = render(
      <StockSelector stocks={manyStocks} value="" onChange={mockOnChange} />
    );

    const options = container.querySelectorAll("option");
    // +1 は placeholder "銘柄を選択してください"
    expect(options.length).toBe(201);
  });
});
