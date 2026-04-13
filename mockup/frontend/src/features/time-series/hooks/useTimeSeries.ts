import { useEffect, useState } from "react";

import { getTimeSeries } from "../api/getTimeSeries";
import type { TimeSeriesRow } from "../types/timeSeries";

type Params = {
  code: string;
  market?: string;
  start: string;
  end: string;
};

export function useTimeSeries(params: Params) {
  const [rows, setRows] = useState<TimeSeriesRow[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;

    if (!params.code || !params.start || !params.end) {
      setRows([]);
      setError(null);
      setIsLoading(false);
      return () => {
        active = false;
      };
    }

    setIsLoading(true);
    setError(null);

    getTimeSeries(params)
      .then((data) => {
        if (!active) {
          return;
        }
        setRows(data.results);
      })
      .catch((err: Error) => {
        if (!active) {
          return;
        }
        setError(err.message);
      })
      .finally(() => {
        if (active) {
          setIsLoading(false);
        }
      });

    return () => {
      active = false;
    };
  }, [params.code, params.market, params.start, params.end]);

  return { rows, isLoading, error };
}