function formatSeconds(value) {
  if (value == null) {
    return "Unavailable";
  }

  if (value < 60) {
    return `${Math.round(value)} sec`;
  }

  if (value < 3600) {
    return `${Math.round(value / 60)} min`;
  }

  return `${(value / 3600).toFixed(1)} hr`;
}

export default function MethodologyPanel({ currentData, analysis, quality }) {
  if (!currentData || !analysis || !quality) {
    return null;
  }

  const assumptions = [
    "Demand gap = total generation - demand.",
    "Reserve margin = demand gap / demand.",
    "Renewable share uses hydro + wind + solar only.",
  ];

  return (
    <section className="grid gap-6 xl:grid-cols-[1.15fr_0.85fr]">
      <article className="rounded-[28px] border border-slate-800 bg-slate-900/75 p-6 shadow-glow">
        <p className="text-xs uppercase tracking-[0.32em] text-teal-300">Methodology</p>
        <h2 className="mt-2 text-2xl font-semibold text-white">Transparent calculation notes</h2>
        <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-400">
          This section makes the analytical assumptions explicit so the project can be defended as
          a measurement workflow rather than a purely visual dashboard.
        </p>

        <div className="mt-6 grid gap-3">
          {assumptions.map((assumption) => (
            <div
              key={assumption}
              className="rounded-2xl border border-slate-800 bg-slate-950/70 px-4 py-3 text-sm text-slate-300"
            >
              {assumption}
            </div>
          ))}
        </div>
      </article>

      <article className="rounded-[28px] border border-slate-800 bg-slate-900/75 p-6 shadow-glow">
        <p className="text-xs uppercase tracking-[0.32em] text-sky-300">Quality Controls</p>
        <h2 className="mt-2 text-2xl font-semibold text-white">Source and freshness audit</h2>

        <div className="mt-6 grid gap-3 text-sm text-slate-300">
          <div className="rounded-2xl border border-slate-800 bg-slate-950/70 px-4 py-3">
            <p className="text-[11px] uppercase tracking-[0.28em] text-slate-500">Source mode</p>
            <p className="mt-2 text-base font-medium capitalize text-white">{quality.source_mode}</p>
          </div>

          <div className="rounded-2xl border border-slate-800 bg-slate-950/70 px-4 py-3">
            <p className="text-[11px] uppercase tracking-[0.28em] text-slate-500">Sample freshness</p>
            <p className="mt-2 text-base font-medium text-white">
              {quality.freshness_label} · {formatSeconds(quality.freshness_seconds)}
            </p>
          </div>

          <div className="rounded-2xl border border-slate-800 bg-slate-950/70 px-4 py-3">
            <p className="text-[11px] uppercase tracking-[0.28em] text-slate-500">Source timestamp age</p>
            <p className="mt-2 text-base font-medium text-white">{formatSeconds(quality.source_age_seconds)}</p>
          </div>
        </div>
      </article>
    </section>
  );
}
