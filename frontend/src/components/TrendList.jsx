const badgeTone = {
  up: "bg-emerald-500/15 text-emerald-300 border-emerald-500/30",
  down: "bg-rose-500/15 text-rose-300 border-rose-500/30",
  steady: "bg-slate-500/15 text-slate-300 border-slate-500/30",
};

const directionLabel = {
  up: "Rising",
  down: "Falling",
  steady: "Stable",
};

const accentTone = {
  Demand: "from-amber-400/25 via-amber-400/5 to-transparent border-amber-400/20",
  Frequency: "from-cyan-400/25 via-cyan-400/5 to-transparent border-cyan-400/20",
  Thermal: "from-rose-400/25 via-rose-400/5 to-transparent border-rose-400/20",
  Renewables: "from-emerald-400/25 via-emerald-400/5 to-transparent border-emerald-400/20",
};

function formatDelta(trend) {
  return `${trend.delta > 0 ? "+" : ""}${trend.delta} ${trend.unit}`;
}

export default function TrendList({ trends }) {
  return (
    <section className="rounded-[28px] border border-slate-800 bg-slate-900/75 p-6 shadow-glow">
      <p className="text-xs uppercase tracking-[0.32em] text-violet-300">Bottom · Trends</p>
      <div className="mt-2">
        <h2 className="text-xl font-semibold text-white">5-second trend snapshots</h2>
        <p className="mt-2 max-w-xl text-sm leading-6 text-slate-400">
          A compact view of short-term movement across the latest backend samples.
          Stable values stay calm, while changes surface immediately through the delta panel.
        </p>
      </div>

      <div className="mt-6 grid gap-4 sm:grid-cols-2">
        {trends.map((trend) => (
          <article
            key={trend.label}
            className={`rounded-[24px] border bg-gradient-to-br p-5 ${
              accentTone[trend.label] || "from-slate-800/70 via-slate-900/50 to-transparent border-slate-700"
            }`}
          >
            <div className="flex items-start justify-between gap-4">
              <div>
                <p className="text-xs uppercase tracking-[0.3em] text-slate-500">Signal</p>
                <h3 className="mt-2 text-lg font-semibold text-white">{trend.label}</h3>
              </div>
              <span
                className={`inline-flex rounded-full border px-3 py-1 text-xs ${badgeTone[trend.direction]}`}
              >
                {directionLabel[trend.direction]}
              </span>
            </div>

            <div className="mt-6">
              <p className="text-4xl font-semibold leading-none text-white break-words">
                {trend.value.toLocaleString()}
              </p>
              <p className="mt-2 text-sm uppercase tracking-[0.28em] text-slate-400">{trend.unit}</p>
            </div>

            <div className="mt-5 rounded-2xl border border-slate-700/80 bg-slate-950/60 px-4 py-3">
              <p className="text-[11px] uppercase tracking-[0.28em] text-slate-500">Delta</p>
              <p className="mt-2 text-lg font-medium text-slate-100 break-words">{formatDelta(trend)}</p>
            </div>

            <div className="mt-5 h-2 overflow-hidden rounded-full bg-slate-800/80">
              <div
                className={`h-full rounded-full transition-all duration-500 ${
                  trend.direction === "up"
                    ? "bg-emerald-400"
                    : trend.direction === "down"
                      ? "bg-rose-400"
                      : "bg-slate-500"
                }`}
                style={{
                  width:
                    trend.direction === "steady"
                      ? "36%"
                      : `${Math.min(100, 36 + Math.abs(trend.delta) * 4)}%`,
                }}
              />
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}
