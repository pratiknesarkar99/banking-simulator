// components/AccountsTable.tsx
import { useAccounts } from "../hooks/useBanking";

export function AccountsTable({
    selected,
    onSelect,
}: {
    selected: string | null;
    onSelect: (id: string) => void;
}) {
    const { data, isLoading } = useAccounts();
    if (isLoading) return <section className="panel"><h2>Accounts</h2><p className="hint">Loading…</p></section>;
    return (
        <section className="panel">
            <h2>Accounts</h2>
            {data?.length === 0 ? (
                <p className="hint">No accounts yet. Create one to get started.</p>
            ) : (
                <table>
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th className="num">Balance</th>
                            <th className="num">Outgoing</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        {data?.map((a) => (
                            <tr
                                key={a.account_id}
                                className={[
                                    a.account_id === selected ? "selected" : "",
                                    a.merged_into ? "merged" : "",
                                ].join(" ")}
                                onClick={() => onSelect(a.account_id)}
                            >
                                <td>{a.account_id}</td>
                                <td className="num">{a.balance.toLocaleString()}</td>
                                <td className="num">{a.total_outgoing.toLocaleString()}</td>
                                <td>
                                    {a.merged_into ? (
                                        <span className="badge merged">→ {a.merged_into}</span>
                                    ) : (
                                        <span className="badge active">active</span>
                                    )}
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            )}
        </section>
    );
}