import React, { useEffect, useState } from 'react';
import { getLiveStatus, closeOrder } from '../api';

export default function PositionsTable() {
  const [positions, setPositions] = useState([]);
  useEffect(() => {
    getLiveStatus().then(status => setPositions(status.open_positions || []));
  }, []);
  if (!positions.length) return <div>Nessuna posizione aperta</div>;
  return (
    <table>
      <thead>
        <tr>
          <th>Ticket</th><th>Simbolo</th><th>Tipo</th><th>Volume</th><th>Prezzo Open</th><th>Prezzo Attuale</th><th>P&L</th><th>SL</th><th>TP</th><th>Azioni</th>
        </tr>
      </thead>
      <tbody>
        {positions.map(pos => (
          <tr key={pos.ticket}>
            <td>{pos.ticket}</td>
            <td>{pos.symbol}</td>
            <td>{pos.type}</td>
            <td>{pos.volume}</td>
            <td>{pos.price_open}</td>
            <td>{pos.price_current}</td>
            <td>{pos.profit}</td>
            <td>{pos.sl}</td>
            <td>{pos.tp}</td>
            <td>
              <button onClick={() => closeOrder({ ticket: pos.ticket })}>Chiudi</button>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
