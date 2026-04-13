import { ErrorMessage } from "../../../components/common/ErrorMessage";
import { Loading } from "../../../components/common/Loading";
import type { SelectorCriteria } from "../../stocks/components/Selector";
import { useTimeSeries } from "../hooks/useTimeSeries";
import type { TimeSeriesRow } from "../types/timeSeries";

type TimeSeriesProps = {
    criteria: SelectorCriteria;
};

type Point = {
    x: number;
    y: number;
};

function buildPath(points: Point[]) {
    if (points.length === 0) {
        return "";
    }
    return points.map((p, i) => `${i === 0 ? "M" : "L"}${p.x.toFixed(2)},${p.y.toFixed(2)}`).join(" ");
}

function finiteValues(values: Array<number | null | undefined>) {
    return values.filter((v): v is number => typeof v === "number" && Number.isFinite(v));
}

function scaleY(value: number, min: number, max: number, top: number, bottom: number) {
    if (max === min) {
        return (top + bottom) / 2;
    }
    const ratio = (value - min) / (max - min);
    return bottom - ratio * (bottom - top);
}

function TimeSeriesChart({ rows, code }: { rows: TimeSeriesRow[]; code: string }) {
    const width = 1100;
    const height = 720;
    const left = 56;
    const right = width - 20;
    const top = 20;
    const priceTop = top;
    const priceBottom = 390;
    const macdTop = 420;
    const macdBottom = 530;
    const rciTop = 545;
    const rciBottom = 620;
    const volTop = 635;
    const volBottom = 700;
    const usableW = Math.max(1, right - left);
    const stepX = rows.length > 1 ? usableW / (rows.length - 1) : usableW;
    const xOf = (i: number) => left + i * stepX;

    const priceMin = Math.min(...rows.map((r) => r.low));
    const priceMax = Math.max(...rows.map((r) => r.high));
    const pad = (priceMax - priceMin) * 0.06;
    const priceRangeMin = priceMin - pad;
    const priceRangeMax = priceMax + pad;

    const macdSeries = finiteValues(rows.flatMap((r) => [r.macd, r.macd_signal, r.hist]));
    const macdAbs = macdSeries.length > 0 ? Math.max(...macdSeries.map((v) => Math.abs(v))) : 1;
    const macdMin = -macdAbs;
    const macdMax = macdAbs;
    const macdZeroY = scaleY(0, macdMin, macdMax, macdTop, macdBottom);

    const volumeMax = Math.max(1, ...rows.map((r) => r.volume));

    const ma5Path = buildPath(
        rows
            .map((r, i) => {
                if (typeof r.ma5 !== "number") {
                    return null;
                }
                return {
                    x: xOf(i),
                    y: scaleY(r.ma5, priceRangeMin, priceRangeMax, priceTop, priceBottom),
                };
            })
            .filter((p): p is Point => p !== null)
    );

    const ma25Path = buildPath(
        rows
            .map((r, i) => {
                if (typeof r.ma25 !== "number") {
                    return null;
                }
                return {
                    x: xOf(i),
                    y: scaleY(r.ma25, priceRangeMin, priceRangeMax, priceTop, priceBottom),
                };
            })
            .filter((p): p is Point => p !== null)
    );

    const macdPath = buildPath(
        rows
            .map((r, i) => {
                if (typeof r.macd !== "number") {
                    return null;
                }
                return {
                    x: xOf(i),
                    y: scaleY(r.macd, macdMin, macdMax, macdTop, macdBottom),
                };
            })
            .filter((p): p is Point => p !== null)
    );

    const signalPath = buildPath(
        rows
            .map((r, i) => {
                if (typeof r.macd_signal !== "number") {
                    return null;
                }
                return {
                    x: xOf(i),
                    y: scaleY(r.macd_signal, macdMin, macdMax, macdTop, macdBottom),
                };
            })
            .filter((p): p is Point => p !== null)
    );

    const rciPath9 = buildPath(
        rows
            .map((r, i) => {
                if (typeof r.rci9 !== "number") {
                    return null;
                }
                return {
                    x: xOf(i),
                    y: scaleY(r.rci9, -100, 100, rciTop, rciBottom),
                };
            })
            .filter((p): p is Point => p !== null)
    );

    const rciPath26 = buildPath(
        rows
            .map((r, i) => {
                if (typeof r.rci26 !== "number") {
                    return null;
                }
                return {
                    x: xOf(i),
                    y: scaleY(r.rci26, -100, 100, rciTop, rciBottom),
                };
            })
            .filter((p): p is Point => p !== null)
    );

    const latest = rows[rows.length - 1];

    return (
        <section className="panel chart-panel">
            <div className="panel-header">
                <div>
                    <p className="eyebrow">Time Series</p>
                    <h2>{code}</h2>
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

            <svg viewBox={`0 0 ${width} ${height}`} width="100%" role="img" aria-label="時系列チャート">
                <rect x={0} y={0} width={width} height={height} fill="#f4f9ff" />

                <line x1={left} y1={priceBottom} x2={right} y2={priceBottom} stroke="#b7c3d0" strokeWidth="1" />
                <line x1={left} y1={macdBottom} x2={right} y2={macdBottom} stroke="#b7c3d0" strokeWidth="1" />
                <line x1={left} y1={rciBottom} x2={right} y2={rciBottom} stroke="#b7c3d0" strokeWidth="1" />
                <line x1={left} y1={volBottom} x2={right} y2={volBottom} stroke="#b7c3d0" strokeWidth="1" />
                <line x1={left} y1={macdZeroY} x2={right} y2={macdZeroY} stroke="#9aa8b6" strokeWidth="1" strokeDasharray="4 4" />
                <line x1={left} y1={scaleY(0, -100, 100, rciTop, rciBottom)} x2={right} y2={scaleY(0, -100, 100, rciTop, rciBottom)} stroke="#9aa8b6" strokeWidth="1" strokeDasharray="4 4" />

                {rows.map((row, i) => {
                    const x = xOf(i);
                    const openY = scaleY(row.open, priceRangeMin, priceRangeMax, priceTop, priceBottom);
                    const closeY = scaleY(row.close, priceRangeMin, priceRangeMax, priceTop, priceBottom);
                    const highY = scaleY(row.high, priceRangeMin, priceRangeMax, priceTop, priceBottom);
                    const lowY = scaleY(row.low, priceRangeMin, priceRangeMax, priceTop, priceBottom);
                    const bodyTop = Math.min(openY, closeY);
                    const bodyH = Math.max(1, Math.abs(closeY - openY));
                    const color = row.close >= row.open ? "#d14a4a" : "#6f7a85";
                    const candleW = Math.max(2, stepX * 0.56);
                    const histValue = typeof row.hist === "number" ? row.hist : 0;
                    const histY = scaleY(histValue, macdMin, macdMax, macdTop, macdBottom);
                    const volY = scaleY(row.volume, 0, volumeMax, volTop, volBottom);
                    const barW = Math.max(1, stepX * 0.7);

                    return (
                        <g key={`${row.date}-${i}`}>
                            <line x1={x} y1={highY} x2={x} y2={lowY} stroke={color} strokeWidth="1" />
                            <rect x={x - candleW / 2} y={bodyTop} width={candleW} height={bodyH} fill={color} />
                            <rect x={x - barW / 2} y={Math.min(histY, macdZeroY)} width={barW} height={Math.max(1, Math.abs(histY - macdZeroY))} fill="#6b7785" opacity="0.55" />
                            <rect x={x - barW / 2} y={volY} width={barW} height={Math.max(1, volBottom - volY)} fill="#6b7785" opacity="0.7" />
                        </g>
                    );
                })}

                {ma5Path ? <path d={ma5Path} fill="none" stroke="#4169e1" strokeWidth="1.4" /> : null}
                {ma25Path ? <path d={ma25Path} fill="none" stroke="#20b2aa" strokeWidth="1.4" /> : null}
                {macdPath ? <path d={macdPath} fill="none" stroke="#c71585" strokeWidth="1.2" /> : null}
                {signalPath ? <path d={signalPath} fill="none" stroke="#2e8b57" strokeWidth="1.2" /> : null}
                {rciPath9 ? <path d={rciPath9} fill="none" stroke="#c71585" strokeWidth="1.1" /> : null}
                {rciPath26 ? <path d={rciPath26} fill="none" stroke="#2e8b57" strokeWidth="1.1" /> : null}

                <text x={8} y={34} fontSize="12" fill="#34495e">価格</text>
                <text x={8} y={436} fontSize="12" fill="#34495e">MACD</text>
                <text x={8} y={562} fontSize="12" fill="#34495e">RCI</text>
                <text x={8} y={652} fontSize="12" fill="#34495e">Volume</text>

                {rows
                    .filter((_, i) => i % Math.max(1, Math.floor(rows.length / 8)) === 0)
                    .map((row, i) => {
                        const idx = i * Math.max(1, Math.floor(rows.length / 8));
                        const x = xOf(Math.min(idx, rows.length - 1));
                        const label = row.date.slice(5);
                        return (
                            <text key={`${row.date}-label`} x={x} y={height - 6} fontSize="10" textAnchor="middle" fill="#4a5a6a">
                                {label}
                            </text>
                        );
                    })}
            </svg>
        </section>
    );
}

export function TimeSeries({ criteria }: TimeSeriesProps) {
    const { rows, isLoading, error } = useTimeSeries({
        code: criteria.code,
        market: criteria.market || "TSE",
        start: criteria.start,
        end: criteria.end,
    });

    if (!criteria.code) {
        return (
            <div className="panel">
                <h3>Time Series</h3>
                <p>銘柄を選択するとグラフを表示します。</p>
            </div>
        );
    }

    return (
        <div>
            {isLoading ? <Loading /> : null}
            {error ? <ErrorMessage message={error} /> : null}
                        {!isLoading && !error && rows.length === 0 ? (
                            <div className="panel">
                                <h3>Time Series</h3>
                                <p>対象期間のデータがありません。</p>
                            </div>
                        ) : null}
                        {!isLoading && !error && rows.length > 0 ? <TimeSeriesChart rows={rows} code={criteria.code} /> : null}
        </div>
    );
}