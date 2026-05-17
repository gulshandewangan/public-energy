import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

function CustomTooltip({ active, payload, label }) {
  if (!active || !payload?.length) {
    return null;
  }

  return (
    <div className="rounded-2xl border border-slate-700 bg-slate-950/95 px-4 py-3 text-sm shadow-2xl">
      <p className="text-slate-300">{label}</p>
      {payload.map((entry) => (
        <p key={entry.dataKey} style={{ color: entry.color }}>
          {entry.name}: {Number(entry.value).toLocaleString()}
          {entry.dataKey === "frequency" ? " Hz" : " MW"}
        </p>
      ))}
    </div>
  );
}

export default function DemandLineChart({ series }) {
  return (
    <section className="rounded-[28px] border border-slate-800 bg-slate-900/75 p-6 shadow-glow">
      <div className="flex items-center justify-between gap-3">
        <div>
          <p className="text-xs uppercase tracking-[0.32em] text-teal-300">Middle · Charts</p>
          <h2 className="mt-2 text-xl font-semibold text-white">Demand over time</h2>
        </div>
        <p className="text-xs text-slate-400">Latest 50 persisted records</p>
      </div>
      <div className="mt-6 h-72 rounded-3xl border border-slate-800 bg-slate-950/80 p-4">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={series} margin={{ top: 10, right: 8, left: -18, bottom: 0 }}>
            <defs>
              <linearGradient id="demandFill" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#fbbf24" stopOpacity={0.45} />
                <stop offset="95%" stopColor="#fbbf24" stopOpacity={0.02} />
              </linearGradient>
              <linearGradient id="frequencyFill" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#22d3ee" stopOpacity={0.22} />
                <stop offset="95%" stopColor="#22d3ee" stopOpacity={0.01} />
              </linearGradient>
            </defs>
            <CartesianGrid stroke="rgba(148,163,184,0.12)" vertical={false} />
            <XAxis dataKey="timeLabel" tick={{ fill: "#94a3b8", fontSize: 11 }} axisLine={false} tickLine={false} />
            <YAxis yAxisId="left" tick={{ fill: "#94a3b8", fontSize: 11 }} axisLine={false} tickLine={false} width={52} />
            <YAxis yAxisId="right" orientation="right" domain={[49, 51]} tick={{ fill: "#94a3b8", fontSize: 11 }} axisLine={false} tickLine={false} width={42} />
            <Tooltip content={<CustomTooltip />} />
            <Area
              yAxisId="left"
              type="monotone"
              dataKey="demand"
              name="Demand"
              stroke="#fbbf24"
              fill="url(#demandFill)"
              strokeWidth={3}
              animationDuration={850}
            />
            <Area
              yAxisId="right"
              type="monotone"
              dataKey="frequency"
              name="Frequency"
              stroke="#22d3ee"
              fill="url(#frequencyFill)"
              strokeWidth={2}
              animationDuration={950}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </section>
  );
}
