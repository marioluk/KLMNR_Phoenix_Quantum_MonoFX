import React, { useEffect, useState } from 'react';
import { getPerformanceMetrics } from '../api';

export default function PerformanceMetrics() {
  const [metrics, setMetrics] = useState(null);
  useEffect(() => {
    getPerformanceMetrics().then(setMetrics);
  }, []);
  if (!metrics) return <div>Caricamento metriche...</div>;
  return (
    <div className="metrics-widget">
      <h3>Metriche di Performance</h3>
      <ul>
        <li>Win Rate: {metrics.win_rate}%</li>
        <li>Profit Factor: {metrics.profit_factor}</li>
        <li>Numero Trade: {metrics.num_trades}</li>
        <li>Trade Giornalieri: {metrics.daily_trades}</li>
        <li>Max Drawdown: {metrics.max_drawdown}</li>
        <li>Profitto Totale: {metrics.total_profit}</li>
        <li>Rischio Attuale: {metrics.current_risk}</li>
        <li>Rischio Massimo: {metrics.max_risk}</li>
      </ul>
    </div>
  );
}
