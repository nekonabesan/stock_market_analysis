import { useParams } from "react-router-dom";

import { ErrorMessage } from "../components/common/ErrorMessage";
import { Loading } from "../components/common/Loading";
import { StockChart } from "../features/chart/components/StockChart";
import { RiseSignalBadge } from "../features/signals/components/RiseSignalBadge";
import { useTimeSeries } from "../features/time-series/hooks/useTimeSeries";

export function StockChartPage() {
  const { code = "7203" } = useParams();
  const { rows, isLoading, error } = useTimeSeries({
    code,
    market: "TSE",
    start: "2023-01-01",
    end: "2024-12-31",
  });

  const isRise = rows.some((row) => row.rising_condition);

  return (
    <main className="page-grid">
      <section className="panel inline-row">
        <div>
          <p className="eyebrow">Stock Chart</p>
          <h2>{code}</h2>
        </div>
        <RiseSignalBadge active={isRise} />
      </section>
      {isLoading ? <Loading /> : null}
      {error ? <ErrorMessage message={error} /> : null}
      {!isLoading && !error ? <StockChart rows={rows} title={`Stock ${code}`} /> : null}
    </main>
  );
}