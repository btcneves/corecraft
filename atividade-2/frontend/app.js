const POLL_MS = 2000;

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

function fmtTs(ts) {
  if (!ts) return '—';
  return new Date(ts * 1000).toLocaleTimeString('pt-BR');
}

function fmtHash(h) {
  if (!h) return '—';
  return h.slice(0, 12) + '…' + h.slice(-8);
}

async function fetchSummary() {
  const res = await fetch('/api/events/summary');
  if (!res.ok) return;
  const d = await res.json();
  setText('tx-observed',    d.tx_observed.toLocaleString('pt-BR'));
  setText('blocks-observed', d.blocks_observed.toLocaleString('pt-BR'));
  setText('tx-per-second',  `${d.tx_per_second} tx/s`);
  setText('last-event-time', fmtTs(d.last_event_time));
}

async function fetchLatest() {
  const res = await fetch('/api/events/latest');
  if (!res.ok) return;
  const d = await res.json();

  const blockList = document.getElementById('list-blocks');
  if (d.blocks && d.blocks.length > 0) {
    blockList.innerHTML = [...d.blocks].reverse().map(b =>
      `<li><span class="hash">${fmtHash(b.hash)}</span><span class="ts">${fmtTs(b.ts)}</span></li>`
    ).join('');
  }

  const txList = document.getElementById('list-txs');
  if (d.txs && d.txs.length > 0) {
    txList.innerHTML = [...d.txs].reverse().map(t =>
      `<li><span>${fmtHash(t.txid)}</span><span class="ts">${fmtTs(t.ts)}</span></li>`
    ).join('');
  }
}

async function fetchStateComparison() {
  try {
    const res = await fetch('/api/events/state-comparison');
    if (!res.ok) {
      const body = await res.json().catch(() => ({}));
      showError('err-comparison', `Erro ${res.status}: ${body?.detail?.detail || 'node indisponível'}`);
      return;
    }
    hideError('err-comparison');
    const d = await res.json();
    setText('best-block',      fmtHash(d.best_block));
    setText('last-seen-block', fmtHash(d.last_seen_block));

    const banner = document.getElementById('divergence-banner');
    if (d.divergence) {
      banner.classList.remove('hidden');
    } else {
      banner.classList.add('hidden');
    }
  } catch (e) {
    showError('err-comparison', `Falha de rede: ${e.message}`);
  }
}

async function tick() {
  await Promise.all([fetchSummary(), fetchLatest(), fetchStateComparison()]);
  const el = document.getElementById('last-update');
  if (el) el.textContent = `Última atualização: ${new Date().toLocaleTimeString('pt-BR')}`;
}

tick();
setInterval(tick, POLL_MS);
