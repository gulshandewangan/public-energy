import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

function ComparisonTooltip({ active, payload }) {
  if (!active || !payload?.length) {
    return null;
  }

  const item = payload[0].payload;
  return (
    <div className="rounded-2xl border border-slate-700 bg-slate-950/95 px-4 py-3 text-sm shadow-2xl">
      <p className="text-white">{item.source}</p>
      <p className="text-slate-300">{Number(item.mw).toLocaleString()} MW</p>
    </div>
  );
}

export default function SourceComparisonChart({ data }) {
  return (
    <section className="rounded-[28px] border border-slate-800 bg-slate-900/75 p-6 shadow-glow">
      <p className="text-xs uppercase tracking-[0.32em] text-amber-300">Bottom · Charts</p>
      <h2 className="mt-2 text-xl font-semibold text-white">Source comparison</h2>
      <div className="mt-6 h-72 rounded-3xl border border-slate-800 bg-slate-950/80 p-4">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} margin={{ top: 10, right: 10, left: -18, bottom: 0 }}>
            <CartesianGrid stroke="rgba(148,163,184,0.12)" vertical={false} />
            <XAxis dataKey="source" tick={{ fill: "#94a3b8", fontSize: 12 }} axisLine={false} tickLine={false} />
            <YAxis tick={{ fill: "#94a3b8", fontSize: 11 }} axisLine={false} tickLine={false} width={52} />
            <Tooltip content={<ComparisonTooltip />} cursor={{ fill: "rgba(148,163,184,0.08)" }} />
            <Bar dataKey="mw" radius={[12, 12, 0, 0]} animationDuration={800}>
              {data.map((entry) => (
                <Cell key={entry.source} fill={entry.fill} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </section>
  );
}
