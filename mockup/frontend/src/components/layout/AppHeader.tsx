import { Link } from "react-router-dom";

export function AppHeader() {
  return (
    <header className="app-header">
      <div>
        <p className="eyebrow">Mockup</p>
        <h1>Stock Analysis Dashboard Prototype</h1>
      </div>
      <nav className="header-nav">
        <Link to="/">Home</Link>
        <Link to="/stocks/7203">Chart</Link>
        <Link to="/trendlines/7203">Trendlines</Link>
        <Link to="/shoulders/7203">Shoulders</Link>
      </nav>
    </header>
  );
}