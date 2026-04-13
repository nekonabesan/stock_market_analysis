import { useEffect, useState } from "react";

import { getStocks } from "../api/getStocks";
import type { Stock } from "../types/stock";

export function useStocks() {
  const [stocks, setStocks] = useState<Stock[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;

    getStocks()
      .then((data) => {
        if (!active) {
          return;
        }
        setStocks(data.results);
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
  }, []);

  return { stocks, isLoading, error };
}