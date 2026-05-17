function formatValue(value, unit) {
  return `${Number(value).toLocaleString()} ${unit}`;
}

const toneMap = {
  frequency: "from-cyan-500/20 to-sky-500/5 border-cyan-400/20",
  stateUi: "from-violet-500/20 to-fuchsia-500/5 border-violet-400/20",
  demand: "from-amber-500/20 to-orange-500/5 border-amber-400/20",
  thermal: "from-rose-500/20 to-red-500/5 border-rose-400/20",
  thermalIpp: "from-orange-500/20 to-amber-500/5 border-orange-400/20",
  hydro: "from-blue-500/20 to-indigo-500/5 border-blue-400/20",
  wind: "from-emerald-500/20 to-green-500/5 border-emerald-400/20",
  solar: "from-yellow-500/20 to-lime-500/5 border-yellow-300/20",
  pavagada: "from-pink-500/20 to-rose-500/5 border-pink-400/20",
  discomA: "from-sky-500/20 to-cyan-500/5 border-sky-400/20",
  discomB: "from-indigo-500/20 to-violet-500/5 border-indigo-400/20",
  discomC: "from-emerald-500/20 to-teal-500/5 border-emerald-400/20",
  discomD: "from-amber-500/20 to-yellow-500/5 border-amber-400/20",
  discomE: "from-fuchsia-500/20 to-pink-500/5 border-fuchsia-400/20",
};

export default function LiveStatCard({ title, value, unit, tone, subtitle }) {
  return (
    <article
      className={`rounded-3xl border bg-gradient-to-br p-5 shadow-glow backdrop-blur ${
        toneMap[tone] || "from-slate-800 to-slate-900 border-slate-700"
      }`}
    >
      <p className="text-xs uppercase tracking-[0.32em] text-slate-400">{title}</p>
      <div className="mt-4 flex items-end justify-between gap-4">
        <div>
          <h3 className="text-3xl font-semibold text-white">{formatValue(value, unit)}</h3>
          <p className="mt-2 text-sm text-slate-300">{subtitle}</p>
        </div>
      </div>
    </article>
  );
}
