import React, { useEffect, useState } from 'react';
import { getLiveStatus } from '../api';

export default function LiveStatus() {
  const [status, setStatus] = useState(null);
  useEffect(() => {
    getLiveStatus().then(setStatus);
  }, []);
  if (!status) return <div>Caricamento...</div>;
  return (
    <table>
      <thead>
        <tr>
          <th>Simbolo</th><th>Bid</th><th>Ask</th><th>Spread</th>
        </tr>
      </thead>
      <tbody>
        {Object.entries(status.symbols_data).map(([symbol, data]) => (
          <tr key={symbol}>
            <td>{symbol}</td>
            <td>{data.bid}</td>
            <td>{data.ask}</td>
            <td>{data.spread}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
