export type TimeSeriesRow = {
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
  ma5?: number | null;
  ma25?: number | null;
  macd?: number | null;
  macd_signal?: number | null;
  hist?: number | null;
  rci9?: number | null;
  rci26?: number | null;
  rising_condition?: boolean;
};

export type TimeSeriesResponse = {
  results: TimeSeriesRow[];
};