import { useEffect, useMemo, useState } from "react";
import { fetchDailyTrends, fetchEnergyData, fetchHistoricalData } from "../api/client";

const REFRESH_INTERVAL_MS = 5000;

function createTrendSnapshot(previousValue, currentValue) {
  if (previousValue == null) {
    return { delta: 0, direction: "steady" };
  }

  const delta = Number((currentValue - previousValue).toFixed(2));
  const direction = delta > 0 ? "up" : delta < 0 ? "down" : "steady";
  return { delta, direction };
}

function buildChartSeries(records) {
  return [...records]
    .reverse()
    .map((entry) => ({
      id: entry.id,
      timestamp: entry.timestamp,
      timeLabel: new Date(entry.timestamp).toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit",
      }),
      demand: Number(entry.demand),
      frequency: Number(entry.frequency),
      state_ui: Number(entry.state_ui || 0),
      thermal: Number(entry.thermal),
      thermal_ipp: Number(entry.thermal_ipp || 0),
      hydro: Number(entry.hydro),
      wind: Number(entry.wind),
      solar: Number(entry.solar),
      pavagada_kspdcl: Number(entry.pavagada_kspdcl || 0),
      bescom: Number(entry.bescom || 0),
      hescom: Number(entry.hescom || 0),
      gescom: Number(entry.gescom || 0),
      cesc: Number(entry.cesc || 0),
      mescom: Number(entry.mescom || 0),
      renewable: Number((entry.hydro + entry.wind + entry.solar).toFixed(2)),
    }));
}

function deriveAnalysis(data) {
  if (!data) {
    return null;
  }

  if (data.analysis) {
    return data.analysis;
  }

  const totalGeneration = Number(
    (data.thermal + data.thermal_ipp + data.hydro + data.wind + data.solar).toFixed(2)
  );
  const renewableGeneration = Number((data.hydro + data.wind + data.solar).toFixed(2));
  const demandGapMw = Number((totalGeneration - data.demand).toFixed(2));
  const reserveMarginPct = data.demand
    ? Number(((demandGapMw / data.demand) * 100).toFixed(2))
    : 0;

  return {
    total_generation: totalGeneration,
    renewable_generation: renewableGeneration,
    renewable_share_pct: totalGeneration
      ? Number(((renewableGeneration / totalGeneration) * 100).toFixed(2))
      : 0,
    thermal_share_pct: totalGeneration
      ? Number((((data.thermal + data.thermal_ipp) / totalGeneration) * 100).toFixed(2))
      : 0,
    demand_gap_mw: demandGapMw,
    reserve_margin_pct: reserveMarginPct,
    frequency_deviation_hz: Number(Math.abs(data.frequency - 50).toFixed(3)),
    balance_state:
      reserveMarginPct >= 2 ? "surplus" : reserveMarginPct <= -2 ? "deficit" : "tight",
  };
}

function deriveQuality(data, analysis) {
  if (!data || !analysis) {
    return null;
  }

  if (data.quality) {
    return data.quality;
  }

  const sourceMode = data.is_live
    ? "live"
    : data.data_source === "last_stored_fallback"
      ? "cached"
      : "simulated";

  return {
    source_mode: sourceMode,
    confidence_score: sourceMode === "live" ? 0.95 : sourceMode === "cached" ? 0.72 : 0.4,
    confidence_label:
      sourceMode === "live" ? "high" : sourceMode === "cached" ? "moderate" : "exploratory",
    freshness_seconds: 0,
    freshness_label: "fresh",
    source_age_seconds: null,
    coverage_ratio: data.demand
      ? Number((analysis.total_generation / data.demand).toFixed(3))
      : 0,
  };
}

function getStatusLabel(currentData, error) {
  if (error) {
    return "Connection issue";
  }

  if (!currentData) {
    return "Loading";
  }

  if (currentData.is_live) {
    return "Live feed healthy";
  }

  if (currentData.data_source === "last_stored_fallback") {
    return "Cached fallback";
  }

  if (currentData.data_source === "simulated_fallback") {
    return "Simulated fallback";
  }

  return "Unknown source";
}

function buildAnalyticalHighlights(currentData, analysis, quality) {
  if (!currentData || !analysis || !quality) {
    return [];
  }

  return [
    {
      label: "Renewable share",
      value: analysis.renewable_share_pct,
      unit: "%",
      tone: "emerald",
      description: "Share of current generation coming from hydro, wind, and solar.",
    },
    {
      label: "Reserve margin",
      value: analysis.reserve_margin_pct,
      unit: "%",
      tone: analysis.reserve_margin_pct >= 0 ? "sky" : "rose",
      description: "Generation surplus or deficit relative to current demand.",
    },
    {
      label: "Frequency deviation",
      value: analysis.frequency_deviation_hz,
      unit: "Hz",
      tone: analysis.frequency_deviation_hz <= 0.05 ? "teal" : "amber",
      description: "Absolute distance from the nominal 50 Hz operating point.",
    },
    {
      label: "Coverage ratio",
      value: quality.coverage_ratio,
      unit: "x",
      tone: quality.coverage_ratio >= 1 ? "violet" : "orange",
      description: "Total generation divided by demand for the same sample.",
    },
  ];
}

function buildEvidenceNotes(currentData, analysis, quality) {
  if (!currentData || !analysis || !quality) {
    return [];
  }

  const balanceSentence =
    analysis.balance_state === "surplus"
      ? "Generation is currently above measured demand."
      : analysis.balance_state === "deficit"
        ? "Measured generation is below current demand, so the system reads as supply-tight."
        : "Generation and demand are closely matched in the latest sample.";

  const qualitySentence =
    quality.source_mode === "live"
      ? "Values come from the live scrape path and are suitable for near-real-time interpretation."
      : quality.source_mode === "cached"
        ? "The live source was unavailable, so the dashboard fell back to the most recent stored snapshot."
        : "The live source and historical cache were unavailable, so the dashboard is using a simulated placeholder sample.";

  return [
    {
      title: "Balance interpretation",
      body: `${balanceSentence} Demand gap: ${analysis.demand_gap_mw.toLocaleString()} MW.`,
    },
    {
      title: "Quality assessment",
      body: qualitySentence,
    },
    {
      title: "Method note",
      body: "Reserve margin is computed as (generation minus demand) / demand. Renewable share is computed from hydro + wind + solar.",
    },
  ];
}

export default function useDashboardData() {
  const [currentData, setCurrentData] = useState(null);
  const [historicalRecords, setHistoricalRecords] = useState([]);
  const [dailyTrendData, setDailyTrendData] = useState({ records: [], insights: [] });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [lastUpdated, setLastUpdated] = useState("");

  useEffect(() => {
    let isMounted = true;

    const load = async () => {
      try {
        const [nextData, historicalData, nextDailyTrendData] = await Promise.all([
          fetchEnergyData(),
          fetchHistoricalData(),
          fetchDailyTrends(),
        ]);

        if (!isMounted) {
          return;
        }

        setError("");
        setCurrentData((previousData) => ({
          ...nextData,
          trends: {
            frequency: createTrendSnapshot(previousData?.frequency, nextData.frequency),
            state_ui: createTrendSnapshot(previousData?.state_ui, nextData.state_ui || 0),
            demand: createTrendSnapshot(previousData?.demand, nextData.demand),
            thermal: createTrendSnapshot(previousData?.thermal, nextData.thermal),
            thermal_ipp: createTrendSnapshot(
              previousData?.thermal_ipp,
              nextData.thermal_ipp || 0
            ),
            hydro: createTrendSnapshot(previousData?.hydro, nextData.hydro),
            wind: createTrendSnapshot(previousData?.wind, nextData.wind),
            solar: createTrendSnapshot(previousData?.solar, nextData.solar),
          },
        }));
        setHistoricalRecords(historicalData);
        setDailyTrendData(nextDailyTrendData);
        setLastUpdated(nextData.timestamp);
      } catch (requestError) {
        if (!isMounted) {
          return;
        }

        setError(
          requestError.response?.data?.detail ||
            requestError.message ||
            "Unable to fetch live energy data."
        );
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    };

    load();
    const intervalId = window.setInterval(load, REFRESH_INTERVAL_MS);

    return () => {
      isMounted = false;
      window.clearInterval(intervalId);
    };
  }, []);

  const chartSeries = useMemo(() => buildChartSeries(historicalRecords), [historicalRecords]);
  const analysis = useMemo(() => deriveAnalysis(currentData), [currentData]);
  const quality = useMemo(() => deriveQuality(currentData, analysis), [currentData, analysis]);

  const energyMix = useMemo(() => {
    if (!currentData) {
      return [];
    }

    return [
      { name: "Thermal", value: currentData.thermal, fill: "#fb7185" },
      { name: "Thermal IPP", value: currentData.thermal_ipp, fill: "#f97316" },
      { name: "Hydro", value: currentData.hydro, fill: "#60a5fa" },
      { name: "Wind", value: currentData.wind, fill: "#34d399" },
      { name: "Solar", value: currentData.solar, fill: "#facc15" },
    ];
  }, [currentData]);

  const sourceComparison = useMemo(() => {
    if (!currentData) {
      return [];
    }

    return [
      { source: "Thermal", mw: currentData.thermal, fill: "#fb7185" },
      { source: "Thermal IPP", mw: currentData.thermal_ipp, fill: "#f97316" },
      { source: "Hydro", mw: currentData.hydro, fill: "#60a5fa" },
      { source: "Wind", mw: currentData.wind, fill: "#34d399" },
      { source: "Solar", mw: currentData.solar, fill: "#facc15" },
    ];
  }, [currentData]);

  const trends = useMemo(() => {
    if (!currentData?.trends) {
      return [];
    }

    return [
      {
        label: "Demand",
        value: currentData.demand,
        unit: "MW",
        ...currentData.trends.demand,
      },
      {
        label: "Frequency",
        value: currentData.frequency,
        unit: "Hz",
        ...currentData.trends.frequency,
      },
      {
        label: "State UI",
        value: currentData.state_ui,
        unit: "MW",
        ...currentData.trends.state_ui,
      },
      {
        label: "Thermal",
        value: currentData.thermal,
        unit: "MW",
        ...currentData.trends.thermal,
      },
      {
        label: "Thermal IPP",
        value: currentData.thermal_ipp,
        unit: "MW",
        ...currentData.trends.thermal_ipp,
      },
      {
        label: "Renewables",
        value: Number((currentData.hydro + currentData.wind + currentData.solar).toFixed(2)),
        unit: "MW",
        delta: Number(
          (
            currentData.trends.hydro.delta +
            currentData.trends.wind.delta +
            currentData.trends.solar.delta
          ).toFixed(2)
        ),
        direction:
          currentData.trends.hydro.delta +
            currentData.trends.wind.delta +
            currentData.trends.solar.delta >
          0
            ? "up"
            : currentData.trends.hydro.delta +
                  currentData.trends.wind.delta +
                  currentData.trends.solar.delta <
                0
              ? "down"
              : "steady",
      },
    ];
  }, [currentData]);

  const analyticalHighlights = useMemo(
    () => buildAnalyticalHighlights(currentData, analysis, quality),
    [currentData, analysis, quality]
  );

  const evidenceNotes = useMemo(
    () => buildEvidenceNotes(currentData, analysis, quality),
    [currentData, analysis, quality]
  );

  return {
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
    statusLabel: getStatusLabel(currentData, error),
  };
}
