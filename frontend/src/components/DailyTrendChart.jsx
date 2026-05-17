import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

const toneMap = {
  amber: "border-amber-400/25 bg-amber-500/10 text-amber-100",
  sky: "border-sky-400/25 bg-sky-500/10 text-sky-100",
  emerald: "border-emerald-400/25 bg-emerald-500/10 text-emerald-100",
  orange: "border-orange-400/25 bg-orange-500/10 text-orange-100",
  violet: "border-violet-400/25 bg-violet-500/10 text-violet-100",
};

function DailyTooltip({ active, payload, label }) {
  if (!active || !payload?.length) {
    return null;
  }

  return (
    <div className="rounded-2xl border border-slate-700 bg-slate-950/95 px-4 py-3 text-sm shadow-2xl">
      <p className="text-slate-300">{label}</p>
      {payload.map((entry) => (
        <p key={entry.dataKey} style={{ color: entry.color }}>
          {entry.name}: {Number(entry.value).toLocaleString()}
          {entry.dataKey === "renewable_share_pct" ? "%" : " MW"}
        </p>
      ))}
    </div>
  );
}

export default function DailyTrendChart({ records, insights }) {
  return (
    <section className="mt-8 grid gap-6 xl:grid-cols-[1.55fr_0.95fr]">
      <article className="rounded-[28px] border border-slate-800 bg-slate-900/75 p-6 shadow-glow">
        <div className="flex items-center justify-between gap-3">
          <div>
            <p className="text-xs uppercase tracking-[0.32em] text-teal-300">Daily Archive</p>
            <h2 className="mt-2 text-xl font-semibold text-white">Day-to-day trend comparison</h2>
          </div>
          <p className="text-xs text-slate-400">Excel-backed daily storage</p>
        </div>

        <div className="mt-6 h-80 rounded-3xl border border-slate-800 bg-slate-950/80 p-4">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={records} margin={{ top: 10, right: 10, left: -18, bottom: 0 }}>
              <CartesianGrid stroke="rgba(148,163,184,0.12)" vertical={false} />
              <XAxis dataKey="date" tick={{ fill: "#94a3b8", fontSize: 11 }} axisLine={false} tickLine={false} />
              <YAxis yAxisId="left" tick={{ fill: "#94a3b8", fontSize: 11 }} axisLine={false} tickLine={false} width={56} />
              <YAxis yAxisId="right" orientation="right" tick={{ fill: "#94a3b8", fontSize: 11 }} axisLine={false} tickLine={false} width={44} />
              <Tooltip content={<DailyTooltip />} />
              <Legend wrapperStyle={{ color: "#cbd5e1", fontSize: "12px" }} />
              <Line yAxisId="left" type="monotone" dataKey="demand" name="Demand" stroke="#fbbf24" strokeWidth={3} dot={{ r: 3 }} activeDot={{ r: 5 }} />
              <Line yAxisId="left" type="monotone" dataKey="total_generation" name="Total generation" stroke="#38bdf8" strokeWidth={3} dot={{ r: 3 }} activeDot={{ r: 5 }} />
              <Line yAxisId="right" type="monotone" dataKey="renewable_share_pct" name="Renewable share" stroke="#34d399" strokeWidth={2.5} dot={{ r: 2.5 }} activeDot={{ r: 4 }} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </article>

      <article className="rounded-[28px] border border-slate-800 bg-slate-900/75 p-6 shadow-glow">
        <p className="text-xs uppercase tracking-[0.32em] text-amber-300">Daily Insights</p>
        <h2 className="mt-2 text-xl font-semibold text-white">Clear takeaways from recent days</h2>
        <div className="mt-6 grid gap-4">
          {insights.map((insight) => (
            <div
              key={insight.title}
              className={`rounded-[22px] border p-4 ${toneMap[insight.tone] || "border-slate-700 bg-slate-950/70 text-slate-100"}`}
            >
              <p className="text-[11px] uppercase tracking-[0.28em] opacity-75">{insight.title}</p>
              <p className="mt-3 text-3xl font-semibold">{insight.value}</p>
              <p className="mt-3 text-sm leading-6 opacity-85">{insight.detail}</p>
            </div>
          ))}
        </div>
      </article>
    </section>
  );
}
