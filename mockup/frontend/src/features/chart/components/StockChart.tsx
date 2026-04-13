import type { TimeSeriesRow } from "../../time-series/types/timeSeries";

type Props = {
  rows: TimeSeriesRow[];
  title: string;
};

export function StockChart({ rows, title }: Props) {
  const latest = rows[rows.length - 1];

  return (
    <section className="panel chart-panel">
      <div className="panel-header">
        <div>
          <p className="eyebrow">Chart Placeholder</p>
          <h2>{title}</h2>
        </div>
        <div className="stat-grid">
          <div>
            <span>Rows</span>
            <strong>{rows.length}</strong>
          </div>
          <div>
            <span>Latest Close</span>
            <strong>{latest?.close ?? "-"}</strong>
          </div>
          <div>
            <span>Latest MACD</span>
            <strong>{latest?.macd ?? "-"}</strong>
          </div>
        </div>
      </div>
      <div className="chart-placeholder">
        <p>ここに将来のチャートライブラリを実装します。</p>
        <pre>{JSON.stringify(rows.slice(-5), null, 2)}</pre>
      </div>
    </section>
  );
}