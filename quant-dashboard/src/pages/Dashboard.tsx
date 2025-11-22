// src/pages/Dashboard.tsx
import { useEffect, useState } from "react";

// value imports (components)
import { EquityChart } from "../components/EquityChart";
import { MetricsCards } from "../components/MetricsCards";

// type-only imports
import type { EquityPoint } from "../components/EquityChart";
import type { Metrics } from "../components/MetricsCards";

type BacktestResponse = {
  equity_curve: EquityPoint[];
  metrics: Metrics;
};

export function Dashboard() {
  const [data, setData] = useState<BacktestResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchBacktest() {
      try {
        const res = await fetch("http://localhost:8000/backtest/momentum");
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const json = (await res.json()) as BacktestResponse;
        setData(json);
      } catch (err: unknown) {
        if (err instanceof Error) {
            setError(err.message);
        } else {
            setError("Failed to load backtest");
        }
      } finally {
        setLoading(false);
      }
    }

    fetchBacktest();
  }, []);

  if (loading) {
    return <div className="p-6">Loading backtest…</div>;
  }

  if (error || !data) {
    return (
      <div className="p-6 text-red-500">
        Error: {error ?? "No data returned"}
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <header className="border-b border-slate-800 p-4 flex justify-between items-center">
        <h1 className="text-xl font-semibold">Momentum Strategy Dashboard</h1>
        <span className="text-xs text-slate-400">
          BTC/USDT · 1h · Binance
        </span>
      </header>

      <main className="p-4 grid gap-4 grid-cols-1 lg:grid-cols-3">
        <section className="lg:col-span-2 bg-slate-900 rounded-2xl p-4 shadow-md">
          <h2 className="text-sm font-medium mb-2 text-slate-300">
            Equity Curve
          </h2>
          <EquityChart points={data.equity_curve} />
        </section>

        <section className="bg-slate-900 rounded-2xl p-4 shadow-md">
          <h2 className="text-sm font-medium mb-2 text-slate-300">
            Performance Metrics
          </h2>
          <MetricsCards metrics={data.metrics} />
        </section>
      </main>
    </div>
  );
}
