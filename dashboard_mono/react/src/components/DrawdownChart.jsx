import React, { useEffect, useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ReferenceLine } from 'recharts';

const DrawdownChart = () => {
  const [data, setData] = useState([]);
  const [softLimit, setSoftLimit] = useState(-0.05);
  const [hardLimit, setHardLimit] = useState(-0.10);

  useEffect(() => {
    fetch('/api/performance_metrics')
      .then(res => res.json())
      .then(json => {
        setData(json.drawdown_history || []);
        setSoftLimit(json.drawdown_limits?.soft || -0.05);
        setHardLimit(json.drawdown_limits?.hard || -0.10);
      });
  }, []);

  return (
    <div style={{ width: '100%', minHeight: 320, padding: 8 }}>
      <ResponsiveContainer width="100%" height={window.innerWidth < 600 ? 220 : 320}>
        <LineChart data={data} margin={{ top: 20, right: 30, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="timestamp" tick={{ fontSize: window.innerWidth < 600 ? 10 : 12 }} />
          <YAxis domain={[-0.2, 0]} tickFormatter={v => `${(v*100).toFixed(1)}%`} tick={{ fontSize: window.innerWidth < 600 ? 10 : 12 }} />
          <Tooltip formatter={v => [`${(v*100).toFixed(2)}%`, 'Drawdown']} />
          <Legend wrapperStyle={{ fontSize: window.innerWidth < 600 ? 12 : 14 }} />
          <Line type="monotone" dataKey="drawdown" stroke="#e74c3c" name="Drawdown" dot={false} strokeWidth={2} />
          {/* Evidenzia limiti soft/hard con label e colore */}
          <ReferenceLine y={softLimit} stroke="#f1c40f" strokeDasharray="3 3" label={{ value: `Soft Limit (${(softLimit*100).toFixed(1)}%)`, position: 'right', fill: '#f1c40f', fontSize: 12 }} />
          <ReferenceLine y={hardLimit} stroke="#c0392b" strokeDasharray="6 2" label={{ value: `Hard Limit (${(hardLimit*100).toFixed(1)}%)`, position: 'right', fill: '#c0392b', fontSize: 12 }} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default DrawdownChart;
