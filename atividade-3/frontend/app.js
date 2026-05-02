const POLL_TX_MS  = 5000;
const POLL_WAL_MS = 10000;

// txid -> last known state
const trackedTxs = {};

// ── Helpers ───────────────────────────────────────────────────────────────────
function setText(id, val) {
  const el = document.getElementById(id);
  if (el) el.textContent = val;
}
function showError(id, msg) {
  const el = document.getElementById(id);
  if (!el) return;
  el.textContent = msg;
  el.classList.remove('hidden');
}
function hideError(id) {
  const el = document.getElementById(id);
  if (el) el.classList.add('hidden');
}
function fmtHash(h) {
  if (!h) return '—';
  return h.slice(0, 10) + '…' + h.slice(-6);
}
function statusClass(s) {
  return { broadcast: 'status-broadcast', mempool: 'status-mempool',
           confirmed: 'status-confirmed', unknown: 'status-unknown' }[s] || 'status-unknown';
}

// ── Wallet loading ─────────────────────────────────────────────────────────────
async function loadWallets() {
  const sel = document.getElementById('wallet-select');
  try {
    const res = await fetch('/wallets');
    if (!res.ok) { showError('err-wallet', 'Erro ao carregar wallets'); return; }
    const d = await res.json();
    hideError('err-wallet');

    sel.innerHTML = '';
    if (!d.available_wallets || d.available_wallets.length === 0) {
      sel.innerHTML = '<option value="">— Nenhuma wallet encontrada —</option>';
      return;
    }

    d.available_wallets.forEach(w => {
      const opt = document.createElement('option');
      opt.value = w;
      opt.textContent = w + (d.loaded_wallets.includes(w) ? ' (carregada)' : '');
      sel.appendChild(opt);
    });
    sel.disabled = false;

    // Auto-select if only one wallet or if server already has one selected
    const toSelect = d.selected_wallet || (d.available_wallets.length === 1 ? d.available_wallets[0] : null);
    if (toSelect) {
      sel.value = toSelect;
      await selectWallet(toSelect);
    }
  } catch (e) {
    showError('err-wallet', `Falha de rede: ${e.message}`);
  }
}

async function selectWallet(name) {
  hideError('err-wallet');
  const hint = document.getElementById('wallet-hint');
  if (hint) hint.textContent = `Selecionando "${name}"…`;
  try {
    const res = await fetch('/wallet/select', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ wallet: name }),
    });
    if (!res.ok) {
      const b = await res.json().catch(() => ({}));
      showError('err-wallet', `Erro: ${b.detail || res.status}`);
      if (hint) hint.textContent = '';
      return;
    }
    const d = await res.json();
    if (hint) hint.textContent = `Wallet "${d.selected_wallet}" selecionada.`;
    document.getElementById('btn-send').disabled = false;
    await fetchWalletStatus();
  } catch (e) {
    showError('err-wallet', `Falha de rede: ${e.message}`);
  }
}

// ── Wallet status ──────────────────────────────────────────────────────────────
async function fetchWalletStatus() {
  try {
    const res = await fetch('/wallet/status');
    if (!res.ok) {
      const b = await res.json().catch(() => ({}));
      showError('err-status', `Erro ${res.status}: ${b?.detail?.detail || b.detail || 'node indisponível'}`);
      return;
    }
    hideError('err-status');
    const d = await res.json();
    setText('ws-name',    d.wallet || '—');
    setText('ws-balance', d.balance != null ? `${d.balance} BTC` : '—');
    setText('ws-utxos',   d.utxos != null ? d.utxos.toString() : '—');
  } catch (e) {
    showError('err-status', `Falha de rede: ${e.message}`);
  }
}

// ── Send tx ───────────────────────────────────────────────────────────────────
document.getElementById('btn-send').addEventListener('click', async () => {
  const addr = document.getElementById('to-address').value.trim();
  const amt  = parseFloat(document.getElementById('amount').value);
  hideError('err-send');
  const resultEl = document.getElementById('send-result');
  resultEl.classList.add('hidden');

  if (!addr || isNaN(amt) || amt <= 0) {
    showError('err-send', 'Preencha endereço e valor válidos.');
    return;
  }

  try {
    const res = await fetch('/tx/send', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ to_address: addr, amount: amt }),
    });
    const d = await res.json();
    if (!res.ok) {
      showError('err-send', `Erro ${res.status}: ${d?.detail?.detail || d.detail || JSON.stringify(d)}`);
      return;
    }
    resultEl.textContent = `✓ txid: ${d.txid}`;
    resultEl.classList.remove('hidden');
    trackedTxs[d.txid] = { wallet: d.wallet, status: 'broadcast' };
    renderTxTable();
    await fetchWalletStatus();
  } catch (e) {
    showError('err-send', `Falha de rede: ${e.message}`);
  }
});

// ── TX polling ─────────────────────────────────────────────────────────────────
async function pollTxs() {
  const txids = Object.keys(trackedTxs);
  if (txids.length === 0) return;
  await Promise.all(txids.map(async txid => {
    try {
      const res = await fetch(`/tx/${txid}`);
      if (!res.ok) return;
      const d = await res.json();
      trackedTxs[txid] = d;
    } catch (_) {}
  }));
  renderTxTable();
}

function renderTxTable() {
  const txids = Object.keys(trackedTxs);
  const emptyEl = document.getElementById('tx-list-empty');
  const tableEl = document.getElementById('tx-table');
  const tbody   = document.getElementById('tx-tbody');

  if (txids.length === 0) {
    emptyEl.classList.remove('hidden');
    tableEl.classList.add('hidden');
    return;
  }
  emptyEl.classList.add('hidden');
  tableEl.classList.remove('hidden');

  tbody.innerHTML = txids.map(txid => {
    const t = trackedTxs[txid];
    const status = t.status || 'unknown';
    const warn = t.warning
      ? `<span class="warn-badge">⚠ ${t.warning}</span>`
      : '';
    const age = t.age_seconds != null ? `${t.age_seconds}s` : '—';
    return `<tr>
      <td class="txid">${fmtHash(txid)}</td>
      <td>${t.wallet || '—'}</td>
      <td><span class="status-badge ${statusClass(status)}">${status}</span></td>
      <td>${t.confirmations ?? 0}</td>
      <td>${age}</td>
      <td>${t.message || '—'}${warn}</td>
    </tr>`;
  }).join('');
}

// ── Wallet selector event ──────────────────────────────────────────────────────
document.getElementById('wallet-select').addEventListener('change', async e => {
  const w = e.target.value;
  if (w) await selectWallet(w);
});

// ── Init & intervals ───────────────────────────────────────────────────────────
loadWallets();
setInterval(fetchWalletStatus, POLL_WAL_MS);
setInterval(pollTxs, POLL_TX_MS);

setInterval(() => {
  const el = document.getElementById('last-update');
  if (el) el.textContent = `Última atualização: ${new Date().toLocaleTimeString('pt-BR')}`;
}, 2000);
