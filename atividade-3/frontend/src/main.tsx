import React, { FormEvent, useEffect, useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import { RefreshCw, Send, Wallet, WalletCards } from "lucide-react";
import "./styles.css";

type WalletsResponse = {
  available_wallets: string[];
  loaded_wallets: string[];
  selected_wallet: string | null;
};

type WalletStatus = {
  wallet: string;
  balance: number;
  utxos: number;
};

type SendResponse = {
  txid: string;
  wallet: string;
};

type TrackedTx = {
  txid?: string;
  wallet?: string;
  status?: "broadcast" | "mempool" | "confirmed" | "unknown";
  confirmations?: number;
  age_seconds?: number;
  message?: string;
  warning?: string;
};

const POLL_TX_MS = 5000;
const POLL_WALLET_MS = 10000;

function prefix(): string {
  return window.location.pathname.match(/^\/atividade-\d(?=\/|$)/)?.[0] ?? "";
}

function apiPath(path: string): string {
  return `${prefix()}${path}`;
}

async function requestJson<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(apiPath(path), init);
  const body = await response.json().catch(() => ({}));
  if (!response.ok) {
    const detail = body?.detail?.detail ?? body?.detail ?? JSON.stringify(body);
    throw new Error(`Erro ${response.status}: ${detail}`);
  }
  return body as T;
}

function fmtHash(hash: string): string {
  return `${hash.slice(0, 10)}...${hash.slice(-6)}`;
}

function statusLabel(status?: string): string {
  return status ?? "unknown";
}

function App() {
  const [wallets, setWallets] = useState<WalletsResponse | null>(null);
  const [status, setStatus] = useState<WalletStatus | null>(null);
  const [selected, setSelected] = useState("");
  const [toAddress, setToAddress] = useState("");
  const [amount, setAmount] = useState("");
  const [tracked, setTracked] = useState<Record<string, TrackedTx>>({});
  const [walletError, setWalletError] = useState<string | null>(null);
  const [sendError, setSendError] = useState<string | null>(null);
  const [sendResult, setSendResult] = useState<string | null>(null);

  async function loadWallets() {
    try {
      const data = await requestJson<WalletsResponse>("/wallets");
      setWallets(data);
      const next = data.selected_wallet ?? (data.available_wallets.length === 1 ? data.available_wallets[0] : "");
      setSelected(next);
      setWalletError(null);
      if (next) await selectWallet(next);
    } catch (err) {
      setWalletError(err instanceof Error ? err.message : "Falha ao carregar wallets");
    }
  }

  async function selectWallet(wallet: string) {
    if (!wallet) return;
    try {
      const data = await requestJson<{ selected_wallet: string }>("/wallet/select", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ wallet }),
      });
      setSelected(data.selected_wallet);
      setWalletError(null);
      await loadWalletStatus();
    } catch (err) {
      setWalletError(err instanceof Error ? err.message : "Falha ao selecionar wallet");
    }
  }

  async function loadWalletStatus() {
    try {
      const data = await requestJson<WalletStatus>("/wallet/status");
      setStatus(data);
      setWalletError(null);
    } catch (err) {
      setWalletError(err instanceof Error ? err.message : "Falha ao consultar wallet");
    }
  }

  async function sendTx(event: FormEvent) {
    event.preventDefault();
    setSendError(null);
    setSendResult(null);

    const value = Number(amount);
    if (!toAddress.trim() || !Number.isFinite(value) || value <= 0) {
      setSendError("Preencha endereco e valor validos.");
      return;
    }

    try {
      const data = await requestJson<SendResponse>("/tx/send", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ to_address: toAddress.trim(), amount: value }),
      });
      setTracked((current) => ({
        ...current,
        [data.txid]: { txid: data.txid, wallet: data.wallet, status: "broadcast" },
      }));
      setSendResult(`txid: ${data.txid}`);
      await loadWalletStatus();
    } catch (err) {
      setSendError(err instanceof Error ? err.message : "Falha ao enviar transacao");
    }
  }

  async function pollTxs() {
    const txids = Object.keys(tracked);
    if (txids.length === 0) return;

    const updates = await Promise.all(
      txids.map(async (txid) => {
        try {
          return [txid, await requestJson<TrackedTx>(`/tx/${txid}`)] as const;
        } catch {
          return null;
        }
      }),
    );

    setTracked((current) => {
      const next = { ...current };
      for (const update of updates) {
        if (update) next[update[0]] = { ...update[1], txid: update[0] };
      }
      return next;
    });
  }

  useEffect(() => {
    void loadWallets();
  }, []);

  useEffect(() => {
    const walletId = window.setInterval(() => void loadWalletStatus(), POLL_WALLET_MS);
    const txId = window.setInterval(() => void pollTxs(), POLL_TX_MS);
    return () => {
      window.clearInterval(walletId);
      window.clearInterval(txId);
    };
  }, [tracked]);

  const txRows = useMemo(() => Object.entries(tracked).reverse(), [tracked]);

  return (
    <main className="app-shell">
      <header className="topbar">
        <div>
          <span className="eyebrow">CoreCraft / Atividade 3</span>
          <h1>Multi-Wallet + PSBT</h1>
        </div>
        <button className="icon-button" onClick={() => void loadWallets()} aria-label="Atualizar wallets">
          <RefreshCw size={18} />
        </button>
      </header>

      <section className="layout">
        <div className="panel">
          <div className="panel-title"><WalletCards size={20} /><h2>Wallet ativa</h2></div>
          {walletError ? <div className="error-banner">{walletError}</div> : null}
          <label>
            Wallet
            <select value={selected} onChange={(event) => void selectWallet(event.target.value)}>
              <option value="">Selecione</option>
              {wallets?.available_wallets.map((wallet) => (
                <option key={wallet} value={wallet}>
                  {wallet}{wallets.loaded_wallets.includes(wallet) ? " (carregada)" : ""}
                </option>
              ))}
            </select>
          </label>
          <div className="wallet-metrics">
            <span><Wallet size={18} />{status?.wallet ?? "-"}</span>
            <strong>{status?.balance ?? 0} BTC</strong>
            <span>{status?.utxos ?? 0} UTXOs</span>
          </div>
        </div>

        <form className="panel" onSubmit={(event) => void sendTx(event)}>
          <div className="panel-title"><Send size={20} /><h2>Enviar transacao</h2></div>
          {sendError ? <div className="error-banner">{sendError}</div> : null}
          {sendResult ? <div className="success-banner">{sendResult}</div> : null}
          <label>
            Endereco destino
            <input value={toAddress} onChange={(event) => setToAddress(event.target.value)} placeholder="bcrt1..." />
          </label>
          <label>
            Valor BTC
            <input value={amount} onChange={(event) => setAmount(event.target.value)} inputMode="decimal" placeholder="0.001" />
          </label>
          <button className="primary" type="submit" disabled={!selected}>Enviar via PSBT</button>
        </form>
      </section>

      <section className="panel tx-panel">
        <h2>Transacoes rastreadas</h2>
        {txRows.length === 0 ? <p className="empty">Nenhuma transacao enviada nesta sessao.</p> : null}
        {txRows.length > 0 ? (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>TXID</th>
                  <th>Wallet</th>
                  <th>Status</th>
                  <th>Conf.</th>
                  <th>Idade</th>
                  <th>Mensagem</th>
                </tr>
              </thead>
              <tbody>
                {txRows.map(([txid, tx]) => (
                  <tr key={txid}>
                    <td><code>{fmtHash(txid)}</code></td>
                    <td>{tx.wallet ?? "-"}</td>
                    <td><span className={`badge ${statusLabel(tx.status)}`}>{statusLabel(tx.status)}</span></td>
                    <td>{tx.confirmations ?? 0}</td>
                    <td>{tx.age_seconds != null ? `${tx.age_seconds}s` : "-"}</td>
                    <td>{tx.message ?? "-"}{tx.warning ? ` (${tx.warning})` : ""}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : null}
      </section>
    </main>
  );
}

createRoot(document.getElementById("root")!).render(<App />);
