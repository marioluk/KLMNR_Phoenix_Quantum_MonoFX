import React, { useState } from 'react';
import { sendOrder, modifyOrder, closeOrder } from '../api';

export default function OrderManager() {
  const [symbol, setSymbol] = useState('');
  const [volume, setVolume] = useState('');
  const [type, setType] = useState('buy');
  const [sl, setSL] = useState('');
  const [tp, setTP] = useState('');
  const [result, setResult] = useState(null);

  const handleSend = async () => {
    const res = await sendOrder({ symbol, volume, type, sl, tp });
    setResult(res);
  };

  return (
    <div className="order-manager">
      <h3>Gestione Ordini Manuali</h3>
      <input placeholder="Simbolo" value={symbol} onChange={e => setSymbol(e.target.value)} />
      <input placeholder="Volume" value={volume} onChange={e => setVolume(e.target.value)} />
      <select value={type} onChange={e => setType(e.target.value)}>
        <option value="buy">Buy</option>
        <option value="sell">Sell</option>
      </select>
      <input placeholder="Stop Loss" value={sl} onChange={e => setSL(e.target.value)} />
      <input placeholder="Take Profit" value={tp} onChange={e => setTP(e.target.value)} />
      <button onClick={handleSend}>Invia Ordine</button>
      {result && <div>Risultato: {JSON.stringify(result)}</div>}
    </div>
  );
}
