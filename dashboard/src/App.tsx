import { useState } from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { OperationPanel } from "./components/OperationPanel";
import { AccountsTable } from "./components/AccountsTable";
import { TopSpendersChart } from "./components/TopSpendersChart";
import { HistoryChart } from "./components/HistoryChart";

const qc = new QueryClient();

export default function App() {
  const [selected, setSelected] = useState<string | null>(null);
  return (
    <QueryClientProvider client={qc}>
      <main className="grid">
        <OperationPanel />
        <AccountsTable onSelect={setSelected} />
        <TopSpendersChart />
        <HistoryChart accountId={selected} />
      </main>
    </QueryClientProvider>
  );
}