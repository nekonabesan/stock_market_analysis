import { Stock } from "../types/stock";

interface StockSelectorProps {
  stocks: Stock[];
  value: string;
  onChange: (code: string) => void;
}

export function StockSelector({ stocks, value, onChange }: StockSelectorProps) {
  return (
    <div className="form-group">
      <label htmlFor="stock-select">銘柄</label>
      <select
        id="stock-select"
        value={value}
        onChange={(e) => onChange(e.target.value)}
      >
        <option value="">銘柄を選択してください</option>
        {stocks.slice(0, 200).map((stock) => (
          <option key={stock.code} value={stock.code}>
            {(stock.name ?? "銘柄名なし") + " (" + stock.code + ")"}
          </option>
        ))}
      </select>
    </div>
  );
}