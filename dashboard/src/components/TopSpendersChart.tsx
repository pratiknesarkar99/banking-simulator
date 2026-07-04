import {
    BarChart,
    Bar,
    XAxis,
    YAxis,
    Tooltip,
    ResponsiveContainer,
} from "recharts";
import { useAccounts } from "../hooks/useBanking";
import { CHART_COLORS, useTheme } from "../theme";

export function TopSpendersChart() {
    const { data } = useAccounts();
    const { theme } = useTheme();
    const c = CHART_COLORS[theme];

    const ranked = [...(data ?? [])]
        .filter((a) => !a.merged_into && a.total_outgoing > 0)
        .sort(
            (a, b) =>
                b.total_outgoing - a.total_outgoing ||
                a.account_id.localeCompare(b.account_id)
        )
        .slice(0, 5);

    return (
        <section className="panel">
            <h2>Top spenders</h2>
            {ranked.length === 0 ? (
                <p className="hint">No outgoing transactions yet.</p>
            ) : (
                <ResponsiveContainer width="100%" height={220}>
                    <BarChart data={ranked}>
                        <XAxis
                            dataKey="account_id"
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
                            cursor={{ fill: "transparent" }}
                            contentStyle={{
                                background: c.tooltipBg,
                                border: `1px solid ${c.tooltipBorder}`,
                                borderRadius: 6,
                            }}
                        />
                        <Bar
                            dataKey="total_outgoing"
                            fill={c.accent}
                            barSize={48}
                            radius={[4, 4, 0, 0]}
                        />
                    </BarChart>
                </ResponsiveContainer>
            )}
        </section>
    );
}