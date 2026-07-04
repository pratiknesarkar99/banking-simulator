// components/TopSpendersChart.tsx
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";
import { useAccounts } from "../hooks/useBanking";

export function TopSpendersChart() {
    const { data } = useAccounts();
    const ranked = [...(data ?? [])]
        .filter((a) => !a.merged_into)
        .sort((a, b) => b.total_outgoing - a.total_outgoing || a.account_id.localeCompare(b.account_id))
        .slice(0, 5);

    return (
        <section className="panel">
            <h2>Top spenders</h2>
            <ResponsiveContainer width="100%" height={220}>
                <BarChart data={ranked}>
                    <XAxis dataKey="account_id" />
                    <YAxis allowDecimals={false} />
                    <Tooltip />
                    <Bar dataKey="total_outgoing" fill="var(--accent)" />
                </BarChart>
            </ResponsiveContainer>
        </section>
    );
}