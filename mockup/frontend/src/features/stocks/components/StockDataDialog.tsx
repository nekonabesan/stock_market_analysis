import { useMemo, useState } from "react";

import { searchStock } from "../api/searchStock";
import { upsertStockPrice } from "../api/upsertStockPrice";
import type { SearchResponse } from "../types/search";

type StockDataDialogProps = {
  open: boolean;
  onClose: () => void;
  onCompleted: (payload: {
    market: string;
    code: string;
    start: string;
    end: string;
  }) => void;
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
  return {
    start: toYmd(new Date(year, month, 1)),
    end: toYmd(new Date(year, month + 1, 0)),
  };
}

function guessQueryType(value: string): "name" | "code" {
  return /^[A-Za-z0-9.-]+$/.test(value) ? "code" : "name";
}

export function StockDataDialog({ open, onClose, onCompleted }: StockDataDialogProps) {
  const defaultRange = useMemo(() => getThisMonthRange(), []);

  const [market, setMarket] = useState("TSE");
  const [query, setQuery] = useState("");
  const [start, setStart] = useState(defaultRange.start);
  const [end, setEnd] = useState(defaultRange.end);

  const [resolved, setResolved] = useState<SearchResponse | null>(null);
  const [isSearching, setIsSearching] = useState(false);
  const [isAdding, setIsAdding] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);

  if (!open) {
    return null;
  }

  const resetResolved = () => {
    setResolved(null);
    setMessage(null);
  };

  const handleSearch = async () => {
    const trimmed = query.trim();
    if (!trimmed) {
      setError("銘柄名または銘柄コードを入力してください");
      return;
    }

    setIsSearching(true);
    setError(null);
    setMessage(null);

    const type = guessQueryType(trimmed);
    const payload =
      type === "code"
        ? { market, code: trimmed }
        : { market, name: trimmed };

    try {
      const result = await searchStock(payload);
      setResolved(result);
      setMarket(result.market);
      setMessage("銘柄が見つかりました。期間を選択して追加してください。");
    } catch (err) {
      setResolved(null);
      setMessage(null);
      setError(err instanceof Error ? err.message : "検索に失敗しました");
    } finally {
      setIsSearching(false);
    }
  };

  const handleAdd = async () => {
    if (!resolved) {
      setError("先に検索を実行してください");
      return;
    }
    if (!start || !end) {
      setError("開始日と終了日を入力してください");
      return;
    }
    if (start > end) {
      setError("開始日は終了日以前である必要があります");
      return;
    }

    setIsAdding(true);
    setError(null);

    try {
      await upsertStockPrice({
        code: resolved.code,
        market: resolved.market,
        name: resolved.name,
        start,
        end,
      });
      setMessage("銘柄データを追加しました");
      onCompleted({
        market: resolved.market,
        code: resolved.code,
        start,
        end,
      });
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : "追加に失敗しました");
    } finally {
      setIsAdding(false);
    }
  };

  return (
    <div className="dialog-overlay" role="dialog" aria-modal="true" aria-label="銘柄検索ダイアログ">
      <div className="dialog-panel panel">
        <div className="panel-header">
          <h3>Yahoo Finance から銘柄検索</h3>
          <button type="button" onClick={onClose} className="ghost-button">
            閉じる
          </button>
        </div>

        <div className="form-group">
          <label htmlFor="dialog-market">市場</label>
          <select
            id="dialog-market"
            value={market}
            onChange={(e) => {
              setMarket(e.target.value);
              resetResolved();
            }}
          >
            <optgroup label="日本">
              <option value="TSE">TSE（東京証券取引所）</option>
              <option value="JPX">JPX</option>
            </optgroup>
            <optgroup label="北米">
              <option value="NASDAQ">NASDAQ</option>
              <option value="NYSE">NYSE</option>
              <option value="AMEX">AMEX</option>
              <option value="TSX">TSX（トロント）</option>
            </optgroup>
            <optgroup label="欧州">
              <option value="LSE">LSE（ロンドン）</option>
              <option value="CSE">CSE（コペンハーゲン）</option>
              <option value="FRA">FRA（フランクフルト）</option>
              <option value="EPA">EPA（パリ）</option>
              <option value="AMS">AMS（アムステルダム）</option>
              <option value="EBR">EBR（ブリュッセル）</option>
              <option value="STO">STO（ストックホルム）</option>
              <option value="HEL">HEL（ヘルシンキ）</option>
              <option value="OB">OB（オスロ）</option>
              <option value="SWX">SWX（スイス）</option>
              <option value="MCE">MCE（マドリード）</option>
              <option value="BIT">BIT（ミラノ）</option>
              <option value="VIE">VIE（ウィーン）</option>
            </optgroup>
            <optgroup label="アジア・オセアニア">
              <option value="HKEX">HKEX（香港）</option>
              <option value="SSE">SSE（上海）</option>
              <option value="SZSE">SZSE（深セン）</option>
              <option value="ASX">ASX（オーストラリア）</option>
            </optgroup>
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="dialog-query">銘柄名または銘柄コード</label>
          <input
            id="dialog-query"
            type="text"
            value={query}
            onChange={(e) => {
              setQuery(e.target.value);
              resetResolved();
            }}
            placeholder="例: トヨタ自動車 / 7203 / AAPL"
          />
        </div>

        {resolved ? (
          <>
            <div className="form-group">
              <label htmlFor="dialog-start">開始日</label>
              <input
                id="dialog-start"
                type="date"
                value={start}
                onChange={(e) => setStart(e.target.value)}
              />
            </div>
            <div className="form-group">
              <label htmlFor="dialog-end">終了日</label>
              <input
                id="dialog-end"
                type="date"
                value={end}
                onChange={(e) => setEnd(e.target.value)}
              />
            </div>
          </>
        ) : null}

        {error ? <div className="error-panel panel">{error}</div> : null}
        {message ? <div className="panel">{message}</div> : null}

        <div className="dialog-actions">
          {!resolved ? (
            <button type="button" onClick={handleSearch} disabled={isSearching}>
              {isSearching ? "検索中..." : "検索"}
            </button>
          ) : (
            <button type="button" onClick={handleAdd} disabled={isAdding}>
              {isAdding ? "追加中..." : "追加"}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
