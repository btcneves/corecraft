import React, { useEffect, useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import { Activity, Blocks, Clock, RefreshCw, Zap } from "lucide-react";
import "./styles.css";

type FeeDistribution = {
  low: number;
  medium: number;
  high: number;
};

type MempoolSummary = {
  tx_count: number;
  avg_fee_rate: number;
  min_fee_rate: number;
  max_fee_rate: number;
  fee_distribution: FeeDistribution;
};

type BlockchainLag = {
  blocks: number;
  headers: number;
  lag: number;
};

const POLL_MS = 5000;

function apiPath(path: string): string {
  const match = window.location.pathname.match(/^\/atividade-\d(?=\/|$)/);
  return `${match?.[0] ?? ""}${path}`;
}

function formatNumber(value: number): string {
  return value.toLocaleString("pt-BR");
}

async function fetchJson<T>(path: string): Promise<T> {
  const response = await fetch(apiPath(path));
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    const detail = body?.detail?.detail ?? body?.detail ?? "node indisponivel";
    throw new Error(`Erro ${response.status}: ${detail}`);
  }
  return response.json() as Promise<T>;
}

function StatCard({
  icon,
  label,
  value,
}: {
  icon: React.ReactNode;
  label: string;
  value: string;
}) {
  return (
    <section className="stat-card">
      <div className="stat-icon">{icon}</div>
      <div>
        <p>{label}</p>
        <strong>{value}</strong>
      </div>
    </section>
  );
}

function App() {
  const [mempool, setMempool] = useState<MempoolSummary | null>(null);
  const [lag, setLag] = useState<BlockchainLag | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [updatedAt, setUpdatedAt] = useState<Date | null>(null);

  async function refresh() {
    try {
      const [mempoolData, lagData] = await Promise.all([
        fetchJson<MempoolSummary>("/api/mempool/summary"),
        fetchJson<BlockchainLag>("/api/blockchain/lag"),
      ]);
      setMempool(mempoolData);
      setLag(lagData);
      setError(null);
      setUpdatedAt(new Date());
    } catch (err) {
      setError(err instanceof Error ? err.message : "Falha ao atualizar dados");
    }
  }

  useEffect(() => {
    void refresh();
    const id = window.setInterval(refresh, POLL_MS);
    return () => window.clearInterval(id);
  }, []);

  const distribution = useMemo(() => {
    const values = mempool?.fee_distribution ?? { low: 0, medium: 0, high: 0 };
    const total = values.low + values.medium + values.high || 1;
    return {
      values,
      widths: {
        low: `${(values.low / total) * 100}%`,
        medium: `${(values.medium / total) * 100}%`,
        high: `${(values.high / total) * 100}%`,
      },
    };
  }, [mempool]);

  return (
    <main className="app-shell">
      <header className="topbar">
        <div>
          <span className="eyebrow">CoreCraft / Atividade 1</span>
          <h1>Mempool Snapshot</h1>
        </div>
        <button className="icon-button" onClick={() => void refresh()} aria-label="Atualizar">
          <RefreshCw size={18} />
        </button>
      </header>

      {error ? <div className="error-banner">{error}</div> : null}

      <section className="grid">
        <StatCard icon={<Activity size={22} />} label="Transacoes na mempool" value={formatNumber(mempool?.tx_count ?? 0)} />
        <StatCard icon={<Zap size={22} />} label="Fee media" value={`${mempool?.avg_fee_rate ?? 0} sat/vB`} />
        <StatCard icon={<Blocks size={22} />} label="Blocos locais" value={formatNumber(lag?.blocks ?? 0)} />
        <StatCard icon={<Clock size={22} />} label="Lag de headers" value={`${lag?.lag ?? 0} blocos`} />
      </section>

      <section className="panel">
        <div className="panel-heading">
          <h2>Distribuicao de fee rate</h2>
          <span>{updatedAt ? `Atualizado ${updatedAt.toLocaleTimeString("pt-BR")}` : "Aguardando dados"}</span>
        </div>
        <div className="fee-bar" aria-label="Distribuicao de taxas">
          <div className="fee-low" style={{ width: distribution.widths.low }} />
          <div className="fee-medium" style={{ width: distribution.widths.medium }} />
          <div className="fee-high" style={{ width: distribution.widths.high }} />
        </div>
        <div className="fee-grid">
          <span>Baixa: {formatNumber(distribution.values.low)}</span>
          <span>Media: {formatNumber(distribution.values.medium)}</span>
          <span>Alta: {formatNumber(distribution.values.high)}</span>
        </div>
      </section>

      <section className="panel compact">
        <span>Menor fee: {mempool?.min_fee_rate ?? 0} sat/vB</span>
        <span>Maior fee: {mempool?.max_fee_rate ?? 0} sat/vB</span>
        <span>Headers: {formatNumber(lag?.headers ?? 0)}</span>
      </section>
    </main>
  );
}

createRoot(document.getElementById("root")!).render(<App />);
