import AnalysisPanel from "../components/AnalysisPanel";
import DailyTrendChart from "../components/DailyTrendChart";
import DemandLineChart from "../components/DemandLineChart";
import EnergyMixChart from "../components/EnergyMixChart";
import LiveStatCard from "../components/LiveStatCard";
import MethodologyPanel from "../components/MethodologyPanel";
import SourceComparisonChart from "../components/SourceComparisonChart";
import TrendList from "../components/TrendList";
import useDashboardData from "../hooks/useDashboardData";

const statConfig = [
  {
    key: "frequency",
    title: "Grid Frequency",
    unit: "Hz",
    tone: "frequency",
    subtitle: "Stability pulse from the latest read",
  },
  {
    key: "state_ui",
    title: "State UI",
    unit: "MW",
    tone: "stateUi",
    subtitle: "Unscheduled interchange at the latest read",
  },
  {
    key: "demand",
    title: "Live Demand",
    unit: "MW",
    tone: "demand",
    subtitle: "Current system load snapshot",
  },
  {
    key: "thermal",
    title: "Thermal",
    unit: "MW",
    tone: "thermal",
    subtitle: "Baseload generation contribution",
  },
  {
    key: "thermal_ipp",
    title: "Thermal IPP",
    unit: "MW",
    tone: "thermalIpp",
    subtitle: "Independent thermal producer contribution",
  },
  {
    key: "hydro",
    title: "Hydro",
    unit: "MW",
    tone: "hydro",
    subtitle: "Water-powered supply at this moment",
  },
  {
    key: "wind",
    title: "Wind",
    unit: "MW",
    tone: "wind",
    subtitle: "Current wind generation input",
  },
  {
    key: "solar",
    title: "Solar",
    unit: "MW",
    tone: "solar",
    subtitle: "Current solar generation input",
  },
  {
    key: "pavagada_kspdcl",
    title: "Pavagada KSPDCL",
    unit: "MW",
    tone: "pavagada",
    subtitle: "Pavagada supply snapshot",
  },
  {
    key: "bescom",
    title: "BESCOM",
    unit: "MW",
    tone: "discomA",
    subtitle: "Current BESCOM allocation",
  },
  {
    key: "hescom",
    title: "HESCOM",
    unit: "MW",
    tone: "discomB",
    subtitle: "Current HESCOM allocation",
  },
  {
    key: "gescom",
    title: "GESCOM",
    unit: "MW",
    tone: "discomC",
    subtitle: "Current GESCOM allocation",
  },
  {
    key: "cesc",
    title: "CESC",
    unit: "MW",
    tone: "discomD",
    subtitle: "Current CESC allocation",
  },
  {
    key: "mescom",
    title: "MESCOM",
    unit: "MW",
    tone: "discomE",
    subtitle: "Current MESCOM allocation",
  },
];

export default function DashboardPage() {
  const {
    currentData,
    analysis,
    quality,
    chartSeries,
    dailyTrendData,
    energyMix,
    sourceComparison,
    trends,
    analyticalHighlights,
    evidenceNotes,
    loading,
    error,
    lastUpdated,
    statusLabel,
  } = useDashboardData();

  const sourceTimestamp = currentData?.source_timestamp
    ? new Date(currentData.source_timestamp).toLocaleString()
    : null;

  return (
    <main className="mx-auto flex min-h-screen max-w-7xl flex-col px-4 py-8 sm:px-6 lg:px-8">
      <section className="relative overflow-hidden rounded-[32px] border border-teal-500/20 bg-slate-900/75 px-6 py-8 shadow-glow backdrop-blur xl:px-10">
        <div className="absolute inset-0 bg-gradient-to-br from-teal-500/10 via-transparent to-sky-500/10" />
        <div className="relative flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <p className="text-xs uppercase tracking-[0.36em] text-teal-300">Public Energy and Climate Tracker</p>
            <h1 className="mt-4 max-w-3xl text-4xl font-semibold tracking-tight text-white sm:text-5xl">
              A more rigorous public-energy dashboard for measurement, comparison, and critique.
            </h1>
            <p className="mt-4 max-w-2xl text-base text-slate-300">
              The interface now separates observed values from derived indicators, tracks
              freshness, and states the assumptions behind each headline figure.
            </p>
          </div>
          <div className="rounded-3xl border border-slate-800 bg-slate-950/70 px-5 py-4 text-sm text-slate-300">
            <p>Status: {loading ? "Refreshing feed..." : statusLabel}</p>
            <p className="mt-2">API update: {lastUpdated ? new Date(lastUpdated).toLocaleString() : "Waiting for first sample"}</p>
            {currentData && !currentData.is_live && sourceTimestamp ? (
              <p className="mt-2 text-amber-300">Value source time: {sourceTimestamp}</p>
            ) : null}
          </div>
        </div>
        {error ? (
          <div className="relative mt-6 rounded-2xl border border-amber-500/30 bg-amber-500/10 px-4 py-3 text-sm text-amber-100">
            {error}
          </div>
        ) : null}
        {currentData && !currentData.is_live ? (
          <div className="relative mt-4 rounded-2xl border border-amber-500/25 bg-amber-500/10 px-4 py-3 text-sm text-amber-100">
            Live scraping is not currently active. The dashboard is showing fallback values until a real source URL is configured in backend/.env.
          </div>
        ) : null}
      </section>

      <section className="mt-8 grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {currentData ? (
          statConfig.map((stat) => (
            <LiveStatCard
              key={stat.key}
              title={stat.title}
              value={currentData[stat.key]}
              unit={stat.unit}
              tone={stat.tone}
              subtitle={stat.subtitle}
            />
          ))
        ) : (
          Array.from({ length: 14 }).map((_, index) => (
            <div
              key={index}
              className="h-36 animate-pulse rounded-3xl border border-slate-800 bg-slate-900/70"
            />
          ))
        )}
      </section>

      <section className="mt-8 grid gap-6 xl:grid-cols-[1.65fr_1fr]">
        <DemandLineChart series={chartSeries} />
        {energyMix.length ? <EnergyMixChart data={energyMix} /> : null}
      </section>

      <DailyTrendChart
        records={dailyTrendData.records}
        insights={dailyTrendData.insights}
      />

      <section className="mt-8">
        <AnalysisPanel
          analysis={analysis}
          quality={quality}
          highlights={analyticalHighlights}
          evidenceNotes={evidenceNotes}
        />
      </section>

      <section className="mt-8 grid gap-6 xl:grid-cols-[1fr_1fr] 2xl:grid-cols-[1.1fr_0.95fr]">
        {sourceComparison.length ? <SourceComparisonChart data={sourceComparison} /> : null}
        <TrendList trends={trends} />
      </section>

      <section className="mt-8">
        <MethodologyPanel
          currentData={currentData}
          analysis={analysis}
          quality={quality}
        />
      </section>
    </main>
  );
}
