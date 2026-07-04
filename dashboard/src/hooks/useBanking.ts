import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { get, post } from "../api/client";
import type {
    AccountView,
    HistoryPoint,
    OperationResult,
} from "../api/types";

export function useAccounts() {
    return useQuery({
        queryKey: ["accounts"],
        queryFn: () => get<AccountView[]>("/views/accounts"),
    });
}

export function useHistory(accountId: string | null) {
    return useQuery({
        queryKey: ["history", accountId],
        queryFn: () => get<HistoryPoint[]>(`/views/accounts/${accountId}/history`),
        enabled: accountId !== null,
    });
}

export function useOperation() {
    const qc = useQueryClient();
    return useMutation({
        mutationFn: ({ path, body }: { path: string; body: unknown }) =>
            post<OperationResult<unknown>>(`/operations/${path}`, body),
        onSettled: () => qc.invalidateQueries(),
    });
}

export function useClock() {
    return useQuery({
        queryKey: ["clock"],
        queryFn: () => get<{ last_timestamp: number }>("/views/clock"),
    });
}