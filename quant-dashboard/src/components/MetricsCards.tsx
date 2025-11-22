export type Metrics = {
  total_return: number;
  cagr: number;
  max_drawdown: number;
  sharpe: number;
  sortino: number;
};

type Props = {
  metrics: Metrics;
};

function pct(x: number) {
  return (x * 100).toFixed(1) + "%";
}

export function MetricsCards({ metrics }: Props) {
  const items = [
    { label: "Total Return: ", value: pct(metrics.total_return) },
    { label: "CAGR: ", value: pct(metrics.cagr) },
    { label: "Max Drawdown: ", value: pct(metrics.max_drawdown) },
    { label: "Sharpe: ", value: metrics.sharpe.toFixed(2) },
    { label: "Sortino: ", value: metrics.sortino.toFixed(2) },
  ];

  return (
    <div className="grid gap-3 grid-cols-2">
      {items.map((item) => (
        <div
          key={item.label}
          className="rounded-xl bg-slate-800 p-3 flex flex-col gap-1"
        >
          <span className="text-xs text-slate-400">{item.label}</span>
          <span className="text-lg font-semibold">{item.value}</span>
        </div>
      ))}
    </div>
  );
}
