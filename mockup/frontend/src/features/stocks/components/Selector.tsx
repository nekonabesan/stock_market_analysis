import { useEffect, useMemo, useState } from "react";

import { ErrorMessage } from "../../../components/common/ErrorMessage";
import { Loading } from "../../../components/common/Loading";
import { useStocks } from "../hooks/useStocks";
import { MarketSelector } from "./MarketSelector";
import { StockSelector } from "./StockSelector";
import { Start } from "./Start";
import { End } from "./End";

export type SelectorCriteria = {
  market: string;
  code: string;
  start: string;
  end: string;
};

type SelectorProps = {
  onChange: (criteria: SelectorCriteria) => void;
};

function toYmd(date: Date) {
  const yyyy = date.getFullYear();
  const mm = String(date.getMonth() + 1).padStart(2, "0");
  const dd = String(date.getDate()).padStart(2, "0");
  return `${yyyy}-${mm}-${dd}`;
}

function getThisMonthRange() {
  const now = new Date();
  const year = now.getFullYear();
  const month = now.getMonth();
  const first = new Date(year, month, 1);
  const last = new Date(year, month + 1, 0);
  return {
    start: toYmd(first),
    end: toYmd(last),
  };
}

export function Selector({ onChange }: SelectorProps) {
  const monthRange = useMemo(() => getThisMonthRange(), []);
  const { stocks, isLoading, error } = useStocks();
  const [selectedMarket, setSelectedMarket] = useState("");
  const [selectedCode, setSelectedCode] = useState("");
  const [startDate, setStartDate] = useState(monthRange.start);
  const [endDate, setEndDate] = useState(monthRange.end);

  const filteredStocks =
    selectedMarket === ""
      ? stocks
      : stocks.filter((stock) => stock.market === selectedMarket);

  useEffect(() => {
    onChange({
      market: selectedMarket,
      code: selectedCode,
      start: startDate,
      end: endDate,
    });
  }, [onChange, selectedMarket, selectedCode, startDate, endDate]);

  useEffect(() => {
    if (selectedCode === "") {
      return;
    }
    const existsInFilter = filteredStocks.some((stock) => stock.code === selectedCode);
    if (!existsInFilter) {
      setSelectedCode("");
    }
  }, [filteredStocks, selectedCode]);

  if (isLoading) {
    return <Loading />;
  }

  if (error) {
    return <ErrorMessage message={error} />;
  }

  return (
    <div className="panel">
      <h2>データセレクタ</h2>
      <MarketSelector
        stocks={stocks}
        value={selectedMarket}
        onChange={setSelectedMarket}
      />
      <StockSelector
        stocks={filteredStocks}
        value={selectedCode}
        onChange={setSelectedCode}
      />
      <Start value={startDate} onChange={setStartDate} />
      <End value={endDate} onChange={setEndDate} />
    </div>
  );
}
