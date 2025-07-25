import React, { useEffect, useState } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const SymbolPerformanceChart = () => {
  const [data, setData] = useState([]);

  useEffect(() => {
    fetch('/api/performance_metrics')
      .then(res => res.json())
      .then(json => setData(json.symbol_performance || []));
  }, []);

  return (
    <div style={{ width: '100%', minHeight: 320, padding: 8 }}>
      <ResponsiveContainer width="100%" height={window.innerWidth < 600 ? 220 : 320}>
        <BarChart data={data} margin={{ top: 20, right: 30, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="symbol" tick={{ fontSize: window.innerWidth < 600 ? 10 : 12 }} />
          <YAxis tick={{ fontSize: window.innerWidth < 600 ? 10 : 12 }} />
          <Tooltip formatter={(v, k) => k === 'pl' ? [`${v.toLocaleString('it-IT', {minimumFractionDigits:2})} €`, 'P&L'] : [v, k]} />
          <Legend wrapperStyle={{ fontSize: window.innerWidth < 600 ? 12 : 14 }} />
          <Bar dataKey="pl" fill="#2980b9" name="P&L" />
          <Bar dataKey="trades" fill="#8e44ad" name="N° Trades" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};

export default SymbolPerformanceChart;
