import React, { useEffect, useState } from 'react';
import { getQuantumSignals } from '../api';

export default function QuantumSignals() {
  const [signals, setSignals] = useState({});
  useEffect(() => {
    getQuantumSignals().then(setSignals);
  }, []);
  if (!Object.keys(signals).length) return <div>Nessun segnale quantistico</div>;
  return (
    <table>
      <thead>
        <tr>
          <th>Simbolo</th><th>Entropia</th><th>Spin</th><th>Confidence</th><th>Trend</th><th>Volatilità</th><th>Segnale</th><th>Prezzo</th><th>Timestamp</th>
        </tr>
      </thead>
      <tbody>
        {Object.entries(signals).map(([symbol, s]) => (
          <tr key={symbol}>
            <td>{symbol}</td>
            <td>{s.entropia}</td>
            <td>{s.spin}</td>
            <td>{s.confidence}</td>
            <td>{s.trend}</td>
            <td>{s.volatility}</td>
            <td>{s.signal}</td>
            <td>{s.price}</td>
            <td>{new Date(s.timestamp * 1000).toLocaleString()}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
