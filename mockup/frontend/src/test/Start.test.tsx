import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { Start } from "../features/stocks/components/Start";

describe("Start", () => {
  it("should render with correct label", () => {
    const mockOnChange = vi.fn();
    render(<Start value="" onChange={mockOnChange} />);

    const label = screen.getByText("データ取得開始期間");
    expect(label).toBeInTheDocument();
  });

  it("should call onChange when date is changed", () => {
    const mockOnChange = vi.fn();
    render(<Start value="2024-01-01" onChange={mockOnChange} />);

    const input = screen.getByDisplayValue("2024-01-01") as HTMLInputElement;
    fireEvent.change(input, { target: { value: "2024-03-15" } });

    expect(mockOnChange).toHaveBeenCalledWith("2024-03-15");
  });

  it("should display the start date value", () => {
    const mockOnChange = vi.fn();
    const { rerender } = render(
      <Start value="2024-01-01" onChange={mockOnChange} />
    );

    const input = screen.getByDisplayValue("2024-01-01") as HTMLInputElement;
    expect(input).toHaveValue("2024-01-01");

    rerender(<Start value="2024-06-01" onChange={mockOnChange} />);
    const updatedInput = screen.getByDisplayValue("2024-06-01") as HTMLInputElement;
    expect(updatedInput).toHaveValue("2024-06-01");
  });
});
