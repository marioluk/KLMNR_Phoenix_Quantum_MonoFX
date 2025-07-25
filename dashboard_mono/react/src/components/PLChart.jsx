import React, { useEffect, useState } from 'react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';

const PLChart = () => {
  const [data, setData] = useState([]);

  useEffect(() => {
    fetch('/api/performance_metrics')
      .then(res => res.json())
      .then(json => setData(json.pl_history || []));
  }, []);

  return (
    <div style={{ width: '100%', minHeight: 320, padding: 8 }}>
      <ResponsiveContainer width="100%" height={window.innerWidth < 600 ? 220 : 320}>
        <AreaChart data={data} margin={{ top: 20, right: 30, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="timestamp" tick={{ fontSize: window.innerWidth < 600 ? 10 : 12 }} />
          <YAxis tick={{ fontSize: window.innerWidth < 600 ? 10 : 12 }} />
          <Tooltip formatter={(v, k) => [`${v.toLocaleString('it-IT', {minimumFractionDigits:2})} €`, k]} />
          <Legend wrapperStyle={{ fontSize: window.innerWidth < 600 ? 12 : 14 }} />
          <Area type="monotone" dataKey="pl_cumulative" stroke="#27ae60" fill="#27ae60" name="P&L Cumulativo" strokeWidth={2} />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
};

export default PLChart;
