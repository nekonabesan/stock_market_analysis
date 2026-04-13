import { useParams } from "react-router-dom";

export function ShouldersPage() {
  const { code = "7203" } = useParams();

  return (
    <main className="page-grid">
      <section className="panel">
        <p className="eyebrow">Inverse Head and Shoulders</p>
        <h2>{code}</h2>
        <p>逆三尊パターンの可視化ページをここへ移植します。</p>
      </section>
    </main>
  );
}