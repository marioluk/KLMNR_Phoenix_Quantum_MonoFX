export async function getLiveStatus() {
  const res = await fetch('/api/live_status');
  return await res.json();
}

export async function getTradeHistory() {
  const res = await fetch('/api/trade_history');
  return await res.json();
}

export async function getQuantumSignals() {
  const res = await fetch('/api/quantum_signals');
  return await res.json();
}

export async function closeOrder({ ticket }) {
  const res = await fetch('/api/order/close', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ ticket })
  });
  return await res.json();
}

export async function getPerformanceMetrics() {
  const res = await fetch('/api/performance_metrics');
  return await res.json();
}

export async function modifyOrder({ ticket, sl, tp }) {
  const res = await fetch('/api/order/modify', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ ticket, sl, tp })
  });
  return await res.json();
}

export async function sendOrder({ symbol, type, volume, sl, tp }) {
  const res = await fetch('/api/order', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ symbol, type, size: volume, sl, tp })
  });
  return await res.json();
}