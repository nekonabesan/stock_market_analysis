import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { End } from "../features/stocks/components/End";

describe("End", () => {
  it("should render with correct label", () => {
    const mockOnChange = vi.fn();
    render(<End value="" onChange={mockOnChange} />);

    const label = screen.getByText("データ取得終了期間");
    expect(label).toBeInTheDocument();
  });

  it("should call onChange when date is changed", () => {
    const mockOnChange = vi.fn();
    render(<End value="2024-12-31" onChange={mockOnChange} />);

    const input = screen.getByDisplayValue("2024-12-31") as HTMLInputElement;
    fireEvent.change(input, { target: { value: "2024-11-30" } });

    expect(mockOnChange).toHaveBeenCalledWith("2024-11-30");
  });

  it("should display the end date value", () => {
    const mockOnChange = vi.fn();
    const { rerender } = render(
      <End value="2024-12-31" onChange={mockOnChange} />
    );

    const input = screen.getByDisplayValue("2024-12-31") as HTMLInputElement;
    expect(input).toHaveValue("2024-12-31");

    rerender(<End value="2024-11-30" onChange={mockOnChange} />);
    const updatedInput = screen.getByDisplayValue("2024-11-30") as HTMLInputElement;
    expect(updatedInput).toHaveValue("2024-11-30");
  });
});
