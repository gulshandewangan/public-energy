export default function StatusBanner({ error, total }) {
  if (error) {
    return <div className="status-banner error">{error}</div>;
  }

  return (
    <div className="status-banner">
      Tracking <strong>{total}</strong> latest metric records.
    </div>
  );
}

