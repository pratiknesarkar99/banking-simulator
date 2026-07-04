import { useRef, useState } from "react";
import { useOperation } from "../hooks/useBanking";
import type { OperationName } from "../api/types";

const FIELD_CONFIG: Record<OperationName, string[]> = {
    "create-account": ["account_id"],
    deposit: ["account_id", "amount"],
    transfer: ["source_account_id", "target_account_id", "amount"],
    pay: ["account_id", "amount"],
    "payment-status": ["account_id", "payment_id"],
    merge: ["account_id1", "account_id2"],
    "balance-at": ["account_id", "time_at"],
};

const NUMERIC_FIELDS = new Set(["amount", "time_at"]);

export function OperationPanel() {
    const [op, setOp] = useState<OperationName>("create-account");
    const [fields, setFields] = useState<Record<string, string>>({});
    const [tsOverride, setTsOverride] = useState("");
    const [log, setLog] = useState<string[]>([]);
    const nextTs = useRef(1);
    const { mutateAsync, isPending } = useOperation();

    async function run() {
        const timestamp = tsOverride ? Number(tsOverride) : nextTs.current;
        const body: Record<string, unknown> = { timestamp };
        for (const f of FIELD_CONFIG[op]) {
            body[f] = NUMERIC_FIELDS.has(f) ? Number(fields[f]) : fields[f];
        }
        try {
            const resp = await mutateAsync({ path: op, body });
            nextTs.current = timestamp + 1;
            setTsOverride("");
            setLog((l) =>
                [`t=${timestamp} ${op} → ${JSON.stringify(resp.result)}`, ...l].slice(0, 20)
            );
        } catch (e) {
            setLog((l) => [`t=${timestamp} ${op} ✗ ${(e as Error).message}`, ...l]);
        }
    }

    return (
        <section className="panel">
            <h2>Run operation</h2>
            <select value={op} onChange={(e) => { setOp(e.target.value as OperationName); setFields({}); }}>
                {Object.keys(FIELD_CONFIG).map((name) => (
                    <option key={name} value={name}>{name}</option>
                ))}
            </select>

            {FIELD_CONFIG[op].map((f) => (
                <input
                    key={f}
                    placeholder={f}
                    value={fields[f] ?? ""}
                    onChange={(e) => setFields((prev) => ({ ...prev, [f]: e.target.value }))}
                />
            ))}

            <input
                placeholder={`timestamp (auto: ${nextTs.current})`}
                value={tsOverride}
                onChange={(e) => setTsOverride(e.target.value)}
            />

            <button onClick={run} disabled={isPending}>Execute</button>

            <div className="log">
                {log.map((line, i) => (
                    <code key={i}>{line}</code>
                ))}
            </div>
        </section>
    );
}