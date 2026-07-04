// api/client.ts
const BASE = import.meta.env.VITE_API_URL ?? "http://127.0.0.1:8000";

export async function post<T>(path: string, body: unknown): Promise<T> {
    const resp = await fetch(`${BASE}${path}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
    });
    if (!resp.ok) {
        const detail = await resp.json().catch(() => null);
        throw new Error(detail?.detail?.[0]?.msg ?? `HTTP ${resp.status}`);
    }
    return resp.json();
}

export async function get<T>(path: string): Promise<T> {
    const resp = await fetch(`${BASE}${path}`);
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    return resp.json();
}