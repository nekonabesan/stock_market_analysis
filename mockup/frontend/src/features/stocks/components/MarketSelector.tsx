import { Stock } from "../types/stock";

interface MarketSelectorProps {
  stocks: Stock[];
  value: string;
  onChange: (market: string) => void;
}

export function MarketSelector({ stocks, value, onChange }: MarketSelectorProps) {
  // 市場の一覧を取得（重複を排除）
  const markets = Array.from(
    new Set(stocks.map((stock) => stock.market).filter((market) => market != null))
  ).sort();

  return (
    <div className="form-group">
      <label htmlFor="market-select">市場</label>
      <select
        id="market-select"
        value={value}
        onChange={(e) => onChange(e.target.value)}
      >
        <option value="">すべての市場</option>
        {markets.map((market) => (
          <option key={market} value={market}>
            {market}
          </option>
        ))}
      </select>
    </div>
  );
}