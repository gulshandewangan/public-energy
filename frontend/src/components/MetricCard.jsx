export default function MetricCard({ metric }) {
  return (
    <article className="metric-card">
      <p className="metric-label">{metric.metric_name}</p>
      <h2>
        {metric.value} <span>{metric.unit}</span>
      </h2>
      <p className="metric-meta">{metric.source_name}</p>
      <p className="metric-meta">{metric.region}</p>
      <p className="metric-time">
        Captured: {new Date(metric.captured_at).toLocaleString()}
      </p>
    </article>
  );
}

