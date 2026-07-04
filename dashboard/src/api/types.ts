// api/types.ts
export interface AccountView {
    account_id: string;
    balance: number;
    total_outgoing: number;
    created_at: number;
    merged_into: string | null;
}

export interface HistoryPoint {
    timestamp: number;
    balance: number;
}

export interface SpenderEntry {
    account_id: string;
    total_outgoing: number;
}

export interface OperationResult<T> {
    result: T;
}

export type OperationName =
    | "create-account"
    | "deposit"
    | "transfer"
    | "pay"
    | "payment-status"
    | "merge"
    | "balance-at";