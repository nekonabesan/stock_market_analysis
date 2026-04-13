import { useCallback, useState } from "react";

import { Selector, type SelectorCriteria } from "../features/stocks/components/Selector";
import { TimeSeries } from "../features/time-series/components/TimeSeries";

export function HomePage() {
    const [criteria, setCriteria] = useState<SelectorCriteria>({
        market: "",
        code: "",
        start: "",
        end: "",
    });

    const handleChangeCriteria = useCallback((next: SelectorCriteria) => {
        setCriteria(next);
    }, []);

    return (
        <main className="page-grid">
            <section className="hero panel">
                <p className="eyebrow">React + TypeScript Mockup</p>
                <h2>Flask モックからダッシュボード移行するためのフロントエンド初期構成</h2>
                <div>
                    <div>既存の株価分析 UI を React/TypeScript へ分解し、銘柄一覧・時系列取得・分析表示を段階的に移行できる骨格です。</div>
                    <Selector onChange={handleChangeCriteria} />
                </div>
                <div>
                    <TimeSeries criteria={criteria} />
                </div>
            </section>            
        </main>
    );
}