import {
    LineChart,
    Line,
    XAxis,
    YAxis,
    Tooltip,
    ResponsiveContainer,
} from "recharts";
import { useHistory } from "../hooks/useBanking";
import { CHART_COLORS, useTheme } from "../theme";

export function HistoryChart({ accountId }: { accountId: string | null }) {
    const { data, isLoading } = useHistory(accountId);
    const { theme } = useTheme();
    const c = CHART_COLORS[theme];

    if (accountId === null) {
        return (
            <section className="panel">
                <h2>Balance history</h2>
                <p className="hint">Select an account in the table to view its history.</p>
            </section>
        );
    }

    if (isLoading) {
        return (
            <section className="panel">
                <h2>Balance history</h2>
                <p className="hint">Loading…</p>
            </section>
        );
    }

    return (
        <section className="panel">
            <h2>Balance history: {accountId}</h2>
            <ResponsiveContainer width="100%" height={220}>
                <LineChart data={data ?? []}>
                    <XAxis
                        dataKey="timestamp"
                        type="number"
                        domain={["dataMin", "dataMax"]}
                        tickFormatter={(t) => t.toLocaleString()}
                        tick={{ fill: c.axis, fontSize: 12 }}
                        axisLine={{ stroke: c.grid }}
                        tickLine={false}
                    />
                    <YAxis
                        allowDecimals={false}
                        tick={{ fill: c.axis, fontSize: 12 }}
                        axisLine={{ stroke: c.grid }}
                        tickLine={false}
                    />
                    <Tooltip
                        labelFormatter={(t) => `t = ${Number(t).toLocaleString()}`}
                        formatter={(value) => [value, "balance"]}
                        contentStyle={{
                            background: c.tooltipBg,
                            border: `1px solid ${c.tooltipBorder}`,
                            borderRadius: 6,
                        }}
                    />
                    <Line
                        type="stepAfter"
                        dataKey="balance"
                        stroke={c.accent}
                        dot={{ r: 3, fill: c.accent, stroke: c.accent }}
                        isAnimationActive={false}
                    />
                </LineChart>
            </ResponsiveContainer>
        </section>
    );
}