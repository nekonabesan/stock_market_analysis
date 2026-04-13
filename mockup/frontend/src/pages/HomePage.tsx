import { useCallback, useState } from "react";

import { Selector, type SelectorCriteria } from "../features/stocks/components/Selector";
import { StockDataDialog } from "../features/stocks/components/StockDataDialog";
import { TimeSeries } from "../features/time-series/components/TimeSeries";

export function HomePage() {
    const [criteria, setCriteria] = useState<SelectorCriteria>({
        market: "",
        code: "",
        start: "",
        end: "",
    });
    const [isDialogOpen, setIsDialogOpen] = useState(false);
    const [selectorVersion, setSelectorVersion] = useState(0);

    const handleChangeCriteria = useCallback((next: SelectorCriteria) => {
        setCriteria(next);
    }, []);

    const handleCompleted = useCallback((next: SelectorCriteria) => {
        setCriteria(next);
        setSelectorVersion((prev) => prev + 1);
    }, []);

    return (
        <main className="page-grid">
            <section className="hero panel">
                <p className="eyebrow">React + TypeScript Mockup</p>
                <h2>Flask モックからダッシュボード移行するためのフロントエンド初期構成</h2>
                <div>
                    <div>既存の株価分析 UI を React/TypeScript へ分解し、銘柄一覧・時系列取得・分析表示を段階的に移行できる骨格です。</div>
                    <div className="dialog-open-row">
                        <button type="button" onClick={() => setIsDialogOpen(true)}>
                            銘柄検索 / データ追加
                        </button>
                    </div>
                    <Selector key={selectorVersion} onChange={handleChangeCriteria} />
                </div>
                <div>
                    <TimeSeries criteria={criteria} />
                </div>
            </section>
            <StockDataDialog
                open={isDialogOpen}
                onClose={() => setIsDialogOpen(false)}
                onCompleted={handleCompleted}
            />
        </main>
    );
}