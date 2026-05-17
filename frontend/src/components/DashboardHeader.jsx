export default function DashboardHeader({ onRefresh, loading }) {
  return (
    <header className="hero">
      <div>
        <p className="eyebrow">Live public infrastructure insights</p>
        <h1>Public Energy and Climate Tracker</h1>
        <p className="hero-copy">
          Monitor demand, renewable generation, and grid indicators from public
          sources through a clean, extensible dashboard.
        </p>
      </div>

      <button className="primary-button" onClick={onRefresh} disabled={loading}>
        {loading ? "Refreshing..." : "Refresh Data"}
      </button>
    </header>
  );
}

