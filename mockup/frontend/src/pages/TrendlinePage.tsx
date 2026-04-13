import { useParams } from "react-router-dom";

export function TrendlinePage() {
  const { code = "7203" } = useParams();

  return (
    <main className="page-grid">
      <section className="panel">
        <p className="eyebrow">Trendlines</p>
        <h2>{code}</h2>
        <p>トレンドライン更新フォームとオーバーレイ描画は次の段階で実装します。</p>
      </section>
    </main>
  );
}