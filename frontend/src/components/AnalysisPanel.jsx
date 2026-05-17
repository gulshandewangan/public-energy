const toneMap = {
  emerald: "border-emerald-400/30 bg-emerald-500/10 text-emerald-100",
  sky: "border-sky-400/30 bg-sky-500/10 text-sky-100",
  teal: "border-teal-400/30 bg-teal-500/10 text-teal-100",
  amber: "border-amber-400/30 bg-amber-500/10 text-amber-100",
  violet: "border-violet-400/30 bg-violet-500/10 text-violet-100",
  orange: "border-orange-400/30 bg-orange-500/10 text-orange-100",
  rose: "border-rose-400/30 bg-rose-500/10 text-rose-100",
};

function formatValue(value) {
  return Number(value).toLocaleString([], {
    minimumFractionDigits: 0,
    maximumFractionDigits: 2,
  });
}

export default function AnalysisPanel({ analysis, quality, highlights, evidenceNotes }) {
  if (!analysis || !quality) {
    return null;
  }

  return (
    <section className="rounded-[28px] border border-slate-800 bg-slate-900/75 p-6 shadow-glow">
      <div className="flex flex-col gap-3 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <p className="text-xs uppercase tracking-[0.32em] text-cyan-300">Analytical Layer</p>
          <h2 className="mt-2 text-2xl font-semibold text-white">Interpretation, not just display</h2>
          <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-400">
            The dashboard now exposes derived indicators so the viewer can justify claims
            about supply adequacy, renewable penetration, and data quality from the same sample.
          </p>
        </div>
        <div className="rounded-2xl border border-slate-700 bg-slate-950/70 px-4 py-3 text-sm text-slate-300">
          <p>Balance state: <span className="font-medium text-white">{analysis.balance_state}</span></p>
        </div>
      </div>

      <div className="mt-6 grid gap-4 lg:grid-cols-4">
        {highlights.map((item) => (
          <article
            key={item.label}
            className={`rounded-[22px] border p-4 ${toneMap[item.tone] || "border-slate-700 bg-slate-800/60 text-slate-100"}`}
          >
            <p className="text-[11px] uppercase tracking-[0.28em] opacity-75">{item.label}</p>
            <p className="mt-3 text-3xl font-semibold">
              {formatValue(item.value)} <span className="text-base font-medium opacity-80">{item.unit}</span>
            </p>
            <p className="mt-3 text-sm leading-6 opacity-85">{item.description}</p>
          </article>
        ))}
      </div>

      <div className="mt-6 grid gap-4 lg:grid-cols-3">
        {evidenceNotes.map((note) => (
          <article key={note.title} className="rounded-[22px] border border-slate-800 bg-slate-950/70 p-5">
            <h3 className="text-sm font-semibold uppercase tracking-[0.18em] text-slate-200">
              {note.title}
            </h3>
            <p className="mt-3 text-sm leading-6 text-slate-400">{note.body}</p>
          </article>
        ))}
      </div>
    </section>
  );
}
