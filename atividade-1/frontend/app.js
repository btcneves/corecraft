const POLL_MS = 5000;

function setText(id, value) {
  const el = document.getElementById(id);
  if (el) el.textContent = value;
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

async function fetchMempool() {
  try {
    const res = await fetch('/api/mempool/summary');
    if (!res.ok) {
      const body = await res.json().catch(() => ({}));
      showError('err-mempool', `Erro ${res.status}: ${body?.detail?.detail || 'node indisponível'}`);
      return;
    }
    const d = await res.json();
    hideError('err-mempool');
    setText('tx-count', d.tx_count.toLocaleString('pt-BR'));
    setText('avg-fee', `${d.avg_fee_rate} sat/vB`);
    setText('min-fee', `${d.min_fee_rate} sat/vB`);
    setText('max-fee', `${d.max_fee_rate} sat/vB`);

    const dist = d.fee_distribution;
    const total = (dist.low + dist.medium + dist.high) || 1;
    document.getElementById('bar-low').style.width  = `${(dist.low    / total * 100).toFixed(1)}%`;
    document.getElementById('bar-med').style.width  = `${(dist.medium / total * 100).toFixed(1)}%`;
    document.getElementById('bar-high').style.width = `${(dist.high   / total * 100).toFixed(1)}%`;
    setText('cnt-low',  dist.low.toLocaleString('pt-BR'));
    setText('cnt-med',  dist.medium.toLocaleString('pt-BR'));
    setText('cnt-high', dist.high.toLocaleString('pt-BR'));
  } catch (e) {
    showError('err-mempool', `Falha de rede: ${e.message}`);
  }
}

async function fetchLag() {
  try {
    const res = await fetch('/api/blockchain/lag');
    if (!res.ok) {
      const body = await res.json().catch(() => ({}));
      showError('err-lag', `Erro ${res.status}: ${body?.detail?.detail || 'node indisponível'}`);
      return;
    }
    const d = await res.json();
    hideError('err-lag');
    setText('blocks',  d.blocks.toLocaleString('pt-BR'));
    setText('headers', d.headers.toLocaleString('pt-BR'));
    setText('lag', `${d.lag} blocos`);
  } catch (e) {
    showError('err-lag', `Falha de rede: ${e.message}`);
  }
}

function updateTimestamp() {
  const el = document.getElementById('last-update');
  if (el) el.textContent = `Última atualização: ${new Date().toLocaleTimeString('pt-BR')}`;
}

async function tick() {
  await Promise.all([fetchMempool(), fetchLag()]);
  updateTimestamp();
}

tick();
setInterval(tick, POLL_MS);
