import { useState } from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { OperationPanel } from "./components/OperationPanel";
import { AccountsTable } from "./components/AccountsTable";
import { TopSpendersChart } from "./components/TopSpendersChart";
import { HistoryChart } from "./components/HistoryChart";
import { ThemeProvider, useTheme } from "./theme";
import { useClock } from "./hooks/useBanking";

const qc = new QueryClient();

function ThemeToggle() {
  const { theme, toggle } = useTheme();
  return (
    <button className="theme-toggle" onClick={toggle}>
      {theme === "dark" ? "Light mode" : "Dark mode"}
    </button>
  );
}

function Dashboard() {
  const [selected, setSelected] = useState<string | null>(null);
  const { data: clock } = useClock();
  const [simTime, setSimTime] = useState(0);
  const shownTime = Math.max(simTime, clock?.last_timestamp ?? 0);

  return (
    <>
      <header className="app-header">
        <h1>Banking Simulator</h1>
        <div className="header-right">
          <span className="sim-time">
            time-stamp: t={shownTime.toLocaleString()}
          </span>
          <ThemeToggle />
        </div>
      </header>
      <main className="grid">
        <OperationPanel onExecuted={setSimTime} />
        <div className="observability">
          <AccountsTable selected={selected} onSelect={setSelected} />
          <div className="chart-row">
            <TopSpendersChart />
            <HistoryChart accountId={selected} />
          </div>
        </div>
      </main>
    </>
  );
}

export default function App() {
  return (
    <ThemeProvider>
      <QueryClientProvider client={qc}>
        <Dashboard />
      </QueryClientProvider>
    </ThemeProvider>
  );
}