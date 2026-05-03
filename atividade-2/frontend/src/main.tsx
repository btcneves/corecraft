import React, { useEffect, useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import { Blocks, Radio, RefreshCw, Unplug, Zap } from "lucide-react";
import "./styles.css";

type EventSummary = {
  blocks_observed: number;
  tx_observed: number;
  last_event_time: number | null;
  tx_per_second: number;
};

type BlockEvent = {
  hash: string;
  ts: number;
};

type TxEvent = {
  txid: string;
  ts: number;
};

type LatestEvents = {
  blocks: BlockEvent[];
  txs: TxEvent[];
};

type StateComparison = {
  best_block?: string;
  last_seen_block?: string | null;
  divergence?: boolean | null;
  status?: string;
  message?: string;
  error?: string;
  detail?: string;
};

type WsPayload = {
  summary: EventSummary;
  latest: LatestEvents;
  state_comparison: StateComparison;
};

const POLL_MS = 2000;

function prefix(): string {
  return window.location.pathname.match(/^\/atividade-\d(?=\/|$)/)?.[0] ?? "";
}

function apiPath(path: string): string {
  return `${prefix()}${path}`;
}

function wsUrl(): string {
  const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
  return `${protocol}//${window.location.host}${prefix()}/ws/events`;
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

function fmtTs(ts?: number | null): string {
  return ts ? new Date(ts * 1000).toLocaleTimeString("pt-BR") : "-";
}

function fmtHash(hash?: string | null): string {
  return hash ? `${hash.slice(0, 12)}...${hash.slice(-8)}` : "-";
}

function App() {
  const [summary, setSummary] = useState<EventSummary | null>(null);
  const [latest, setLatest] = useState<LatestEvents>({ blocks: [], txs: [] });
  const [comparison, setComparison] = useState<StateComparison | null>(null);
  const [connection, setConnection] = useState<"connecting" | "ws" | "polling">("connecting");
  const [error, setError] = useState<string | null>(null);

  async function poll() {
    try {
      const [summaryData, latestData, comparisonData] = await Promise.all([
        fetchJson<EventSummary>("/api/events/summary"),
        fetchJson<LatestEvents>("/api/events/latest"),
        fetchJson<StateComparison>("/api/events/state-comparison"),
      ]);
      setSummary(summaryData);
      setLatest(latestData);
      setComparison(comparisonData);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Falha ao consultar eventos");
    }
  }

  useEffect(() => {
    let closed = false;
    let pollId: number | null = null;
    const socket = new WebSocket(wsUrl());

    socket.onopen = () => {
      if (!closed) setConnection("ws");
    };

    socket.onmessage = (event) => {
      const payload = JSON.parse(event.data) as WsPayload;
      setSummary(payload.summary);
      setLatest(payload.latest);
      setComparison(payload.state_comparison);
      setError(payload.state_comparison?.detail ?? null);
    };

    socket.onerror = () => {
      if (!closed) setConnection("polling");
    };

    socket.onclose = () => {
      if (closed) return;
      setConnection("polling");
      void poll();
      pollId = window.setInterval(poll, POLL_MS);
    };

    return () => {
      closed = true;
      socket.close();
      if (pollId) window.clearInterval(pollId);
    };
  }, []);

  const divergence = comparison?.status === "compared" && comparison.divergence === true;
  const blocks = useMemo(() => [...latest.blocks].reverse(), [latest.blocks]);
  const txs = useMemo(() => [...latest.txs].reverse(), [latest.txs]);

  return (
    <main className="app-shell">
      <header className="topbar">
        <div>
          <span className="eyebrow">CoreCraft / Atividade 2</span>
          <h1>Eventos RPC + ZMQ</h1>
        </div>
        <div className={`connection ${connection}`}>
          {connection === "ws" ? <Radio size={16} /> : <Unplug size={16} />}
          <span>{connection === "ws" ? "WebSocket" : connection === "polling" ? "Polling" : "Conectando"}</span>
        </div>
      </header>

      {divergence ? <div className="warning">Divergencia detectada entre ultimo bloco RPC e ultimo bloco ZMQ.</div> : null}
      {error ? <div className="error-banner">{error}</div> : null}

      <section className="metrics">
        <div className="metric"><Zap size={20} /><span>TX observadas</span><strong>{summary?.tx_observed.toLocaleString("pt-BR") ?? "0"}</strong></div>
        <div className="metric"><Blocks size={20} /><span>Blocos observados</span><strong>{summary?.blocks_observed.toLocaleString("pt-BR") ?? "0"}</strong></div>
        <div className="metric"><RefreshCw size={20} /><span>Taxa</span><strong>{summary?.tx_per_second ?? 0} tx/s</strong></div>
        <div className="metric"><Radio size={20} /><span>Ultimo evento</span><strong>{fmtTs(summary?.last_event_time)}</strong></div>
      </section>

      <section className="comparison">
        <h2>Estado comparado</h2>
        <div><span>RPC best block</span><code>{fmtHash(comparison?.best_block)}</code></div>
        <div><span>ZMQ last block</span><code>{fmtHash(comparison?.last_seen_block)}</code></div>
        <p>{comparison?.message ?? (comparison?.status === "compared" ? "Fluxo e estado comparados." : "Aguardando eventos.")}</p>
      </section>

      <section className="lists">
        <EventList title="Blocos recentes" empty="Nenhum bloco ZMQ observado." items={blocks.map((block) => ({ id: block.hash, label: fmtHash(block.hash), ts: fmtTs(block.ts) }))} />
        <EventList title="Transacoes recentes" empty="Nenhuma tx ZMQ observada." items={txs.map((tx) => ({ id: tx.txid, label: fmtHash(tx.txid), ts: fmtTs(tx.ts) }))} />
      </section>
    </main>
  );
}

function EventList({ title, empty, items }: { title: string; empty: string; items: { id: string; label: string; ts: string }[] }) {
  return (
    <section className="panel">
      <h2>{title}</h2>
      {items.length === 0 ? <p className="empty">{empty}</p> : null}
      <ul>
        {items.map((item) => (
          <li key={item.id}><code>{item.label}</code><span>{item.ts}</span></li>
        ))}
      </ul>
    </section>
  );
}

createRoot(document.getElementById("root")!).render(<App />);
