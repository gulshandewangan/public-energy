import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";

function MixTooltip({ active, payload }) {
  if (!active || !payload?.length) {
    return null;
  }

  const item = payload[0].payload;
  return (
    <div className="rounded-2xl border border-slate-700 bg-slate-950/95 px-4 py-3 text-sm shadow-2xl">
      <p className="text-white">{item.name}</p>
      <p className="text-slate-300">{Number(item.value).toLocaleString()} MW</p>
    </div>
  );
}

export default function EnergyMixChart({ data }) {
  const total = data.reduce((sum, item) => sum + item.value, 0);

  return (
    <section className="rounded-[28px] border border-slate-800 bg-slate-900/75 p-6 shadow-glow">
      <p className="text-xs uppercase tracking-[0.32em] text-sky-300">Middle · Charts</p>
      <h2 className="mt-2 text-xl font-semibold text-white">Energy mix</h2>
      <div className="mt-6 h-72 rounded-3xl border border-slate-800 bg-slate-950/80 p-4">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={data}
              dataKey="value"
              nameKey="name"
              innerRadius={62}
              outerRadius={92}
              paddingAngle={3}
              animationDuration={900}
              animationBegin={120}
            >
              {data.map((entry) => (
                <Cell key={entry.name} fill={entry.fill} />
              ))}
            </Pie>
            <Tooltip content={<MixTooltip />} />
          </PieChart>
        </ResponsiveContainer>
      </div>
      <div className="mt-6 space-y-3">
        {data.map((item) => (
          <div key={item.name} className="flex items-center justify-between rounded-2xl bg-slate-950/70 px-4 py-3">
            <div className="flex items-center gap-3">
              <span className="h-3 w-3 rounded-full" style={{ backgroundColor: item.fill }} />
              <span className="text-sm text-slate-200">{item.name}</span>
            </div>
            <div className="text-right">
              <p className="text-sm font-medium text-white">{item.value.toLocaleString()} MW</p>
              <p className="text-xs text-slate-400">{total ? ((item.value / total) * 100).toFixed(1) : 0}% share</p>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
