import React, { useEffect, useState } from 'react';
import { getTradeHistory } from '../api';

export default function TradeHistory() {
  const [history, setHistory] = useState([]);
  useEffect(() => {
    getTradeHistory().then(setHistory);
  }, []);
  if (!history.length) return <div>Nessun trade storico</div>;
  return (
    <table>
      <thead>
        <tr>
          <th>Ticket</th><th>Simbolo</th><th>Tipo</th><th>Volume</th><th>Prezzo</th><th>P&L</th><th>Data</th><th>Commento</th>
        </tr>
      </thead>
      <tbody>
        {history.map(trade => (
          <tr key={trade.ticket}>
            <td>{trade.ticket}</td>
            <td>{trade.symbol}</td>
            <td>{trade.type}</td>
            <td>{trade.volume}</td>
            <td>{trade.price}</td>
            <td>{trade.profit}</td>
            <td>{new Date(trade.time * 1000).toLocaleString()}</td>
            <td>{trade.comment}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
