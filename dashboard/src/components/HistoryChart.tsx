import {
    LineChart,
    Line,
    XAxis,
    YAxis,
    Tooltip,
    ResponsiveContainer,
} from "recharts";
import { useHistory } from "../hooks/useBanking";

export function HistoryChart({ accountId }: { accountId: string | null }) {
    const { data, isLoading } = useHistory(accountId);

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
                <p>Loading…</p>
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
                    />
                    <YAxis allowDecimals={false} />
                    <Tooltip
                        labelFormatter={(t) => `t = ${Number(t).toLocaleString()}`}
                        formatter={(value) => [value, "balance"]}
                    />
                    <Line
                        type="stepAfter"
                        dataKey="balance"
                        stroke="var(--accent)"
                        dot={{ r: 3 }}
                        isAnimationActive={false}
                    />
                </LineChart>
            </ResponsiveContainer>
        </section>
    );
}