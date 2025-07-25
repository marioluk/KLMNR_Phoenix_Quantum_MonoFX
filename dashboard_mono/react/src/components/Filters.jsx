import React, { useState, useEffect } from 'react';

const Filters = ({ symbols, onChange }) => {
  const [symbol, setSymbol] = useState('');
  const [chartType, setChartType] = useState('equity');
  const [fromTime, setFromTime] = useState('');
  const [toTime, setToTime] = useState('');

  useEffect(() => {
    onChange({ symbol, chartType, fromTime, toTime });
  }, [symbol, chartType, fromTime, toTime, onChange]);

  return (
    <div style={{ display: 'flex', gap: '1rem', marginBottom: '1rem' }}>
      <select value={symbol} onChange={e => setSymbol(e.target.value)}>
        <option value=''>Tutti i simboli</option>
        {symbols.map(s => (
          <option key={s} value={s}>{s}</option>
        ))}
      </select>
      <select value={chartType} onChange={e => setChartType(e.target.value)}>
        <option value='equity'>Equity/Bilancio</option>
        <option value='drawdown'>Drawdown</option>
        <option value='pl'>P&L Cumulativo</option>
        <option value='performance'>Performance per Simbolo</option>
      </select>
      <input type='date' value={fromTime} onChange={e => setFromTime(e.target.value)} />
      <input type='date' value={toTime} onChange={e => setToTime(e.target.value)} />
    </div>
  );
};

export default Filters;
