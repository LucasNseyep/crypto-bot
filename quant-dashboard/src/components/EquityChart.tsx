import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

export type EquityPoint = {
  datetime: string;
  equity: number;
};

type Props = {
  points: EquityPoint[];
};

export function EquityChart({ points }: Props) {
  const data = points.map((p) => ({
    ...p,
    label: new Date(p.datetime).toLocaleString(),
  }));

  return (
    <div style={{ height: "280px" }}>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data}>
          <XAxis dataKey="label" hide />
          <YAxis />
          <Tooltip
            formatter={(value: number | string) => Number(value).toFixed(3)}
            labelFormatter={(label) => String(label)}
          />
          <Line
            type="monotone"
            dataKey="equity"
            stroke="#22c55e"
            strokeWidth={2}
            dot={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
