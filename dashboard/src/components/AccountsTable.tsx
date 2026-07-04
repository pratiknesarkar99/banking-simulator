// components/AccountsTable.tsx
import { useAccounts } from "../hooks/useBanking";

export function AccountsTable({ onSelect }: { onSelect: (id: string) => void }) {
    const { data, isLoading } = useAccounts();
    if (isLoading) return <p>Loading…</p>;
    return (
        <section className="panel">
            <h2>Accounts</h2>
            <table>
                <thead>
                    <tr><th>ID</th><th>Balance</th><th>Outgoing</th><th>Status</th></tr>
                </thead>
                <tbody>
                    {data?.map((a) => (
                        <tr key={a.account_id} onClick={() => onSelect(a.account_id)}>
                            <td>{a.account_id}</td>
                            <td>{a.balance}</td>
                            <td>{a.total_outgoing}</td>
                            <td>{a.merged_into ? `→ ${a.merged_into}` : "active"}</td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </section>
    );
}