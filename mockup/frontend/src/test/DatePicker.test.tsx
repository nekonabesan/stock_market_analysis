import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { DatePicker } from "../features/stocks/components/DatePicker";

describe("DatePicker", () => {
  it("should render label and input element", () => {
    const mockOnChange = vi.fn();
    render(
      <DatePicker label="テスト日付" value="" onChange={mockOnChange} />
    );

    const label = screen.getByText("テスト日付");
    expect(label).toBeInTheDocument();

    const input = screen.getByDisplayValue("") as HTMLInputElement;
    expect(input).toBeInTheDocument();
    expect(input).toHaveAttribute("type", "date");
  });

  it("should call onChange when date is changed", () => {
    const mockOnChange = vi.fn();
    render(
      <DatePicker label="テスト日付" value="2024-01-01" onChange={mockOnChange} />
    );

    const input = screen.getByDisplayValue("2024-01-01") as HTMLInputElement;
    fireEvent.change(input, { target: { value: "2024-12-31" } });

    expect(mockOnChange).toHaveBeenCalledWith("2024-12-31");
    expect(mockOnChange).toHaveBeenCalledTimes(1);
  });

  it("should display the date value in input", () => {
    const mockOnChange = vi.fn();
    const { rerender } = render(
      <DatePicker label="テスト日付" value="2024-06-15" onChange={mockOnChange} />
    );

    const input = screen.getByDisplayValue("2024-06-15") as HTMLInputElement;
    expect(input).toHaveValue("2024-06-15");

    rerender(
      <DatePicker label="テスト日付" value="2024-12-25" onChange={mockOnChange} />
    );

    const updatedInput = screen.getByDisplayValue("2024-12-25") as HTMLInputElement;
    expect(updatedInput).toHaveValue("2024-12-25");
  });
});
