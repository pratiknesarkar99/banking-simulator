import { useEffect, useRef, useState } from "react";
import { useClock, useOperation } from "../hooks/useBanking";
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

interface LogEntry {
    t: number;
    text: string;
    error: boolean;
}

export function OperationPanel({
    onExecuted,
}: {
    onExecuted: (t: number) => void;
}) {
    const [op, setOp] = useState<OperationName>("create-account");
    const [fields, setFields] = useState<Record<string, string>>({});
    const [tsOverride, setTsOverride] = useState("");
    const [log, setLog] = useState<LogEntry[]>([]);
    const nextTs = useRef(1);
    const { data: clock } = useClock();
    const { mutateAsync, isPending } = useOperation();

    useEffect(() => {
        if (clock && clock.last_timestamp >= nextTs.current) {
            nextTs.current = clock.last_timestamp + 1;
        }
    }, [clock]);

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
            onExecuted(timestamp);
            setLog((l) =>
                [
                    {
                        t: timestamp,
                        text: `${op} → ${JSON.stringify(resp.result)}`,
                        error: false,
                    },
                    ...l,
                ].slice(0, 20)
            );
        } catch (e) {
            onExecuted(timestamp);
            setLog((l) =>
                [
                    {
                        t: timestamp,
                        text: `${op} ✗ ${(e as Error).message}`,
                        error: true,
                    },
                    ...l,
                ].slice(0, 20)
            );
        }
    }

    return (
        <section className="panel">
            <h2>Run operation</h2>
            <div className="op-form">
                <select
                    value={op}
                    onChange={(e) => {
                        setOp(e.target.value as OperationName);
                        setFields({});
                    }}
                >
                    {Object.keys(FIELD_CONFIG).map((name) => (
                        <option key={name} value={name}>
                            {name}
                        </option>
                    ))}
                </select>

                {FIELD_CONFIG[op].map((f) => (
                    <input
                        key={f}
                        placeholder={f}
                        value={fields[f] ?? ""}
                        onChange={(e) =>
                            setFields((prev) => ({ ...prev, [f]: e.target.value }))
                        }
                    />
                ))}

                <input
                    placeholder={`timestamp (auto: ${nextTs.current})`}
                    value={tsOverride}
                    onChange={(e) => setTsOverride(e.target.value)}
                />

                <button onClick={run} disabled={isPending}>
                    Execute
                </button>
            </div>

            <div className="log">
                {log.length === 0 && (
                    <span className="empty">No operations yet. Run one above.</span>
                )}
                {log.map((entry, i) => (
                    <code key={i} className={entry.error ? "error" : ""}>
                        <span className="ts">t={entry.t}</span> {entry.text}
                    </code>
                ))}
            </div>
        </section>
    );
}