import React, { useEffect, useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ReferenceLine } from 'recharts';

const EquityChart = () => {
  const [data, setData] = useState([]);

  useEffect(() => {
    // Sostituisci con la tua API reale
    fetch('/api/performance_metrics')
      .then(res => res.json())
      .then(json => setData(json.equity_history || []));
  }, []);

  // Target equity (esempio: 10000)
  const targetEquity = 10000;
  return (
    <div style={{ width: '100%', minHeight: 320, padding: 8 }}>
      <ResponsiveContainer width="100%" height={window.innerWidth < 600 ? 220 : 320}>
        <LineChart data={data} margin={{ top: 20, right: 30, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="timestamp" tick={{ fontSize: window.innerWidth < 600 ? 10 : 12 }} />
          <YAxis tick={{ fontSize: window.innerWidth < 600 ? 10 : 12 }} />
          <Tooltip formatter={(v, k) => [`${v.toLocaleString('it-IT', {minimumFractionDigits:2})} €`, k]} />
          <Legend wrapperStyle={{ fontSize: window.innerWidth < 600 ? 12 : 14 }} />
          <Line type="monotone" dataKey="equity" stroke="#8884d8" name="Equity" dot={false} strokeWidth={2} />
          <Line type="monotone" dataKey="balance" stroke="#82ca9d" name="Bilancio" dot={false} strokeWidth={2} />
          {/* Evidenzia target equity */}
          <ReferenceLine y={targetEquity} stroke="#2ecc71" strokeDasharray="5 5" label={{ value: 'Target', position: 'right', fill: '#2ecc71', fontSize: 12 }} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default EquityChart;
