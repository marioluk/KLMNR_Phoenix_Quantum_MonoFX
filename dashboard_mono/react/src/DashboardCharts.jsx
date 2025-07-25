import React, { useState, useEffect } from 'react';
import Filters from './components/Filters';
import EquityChart from './components/EquityChart';
import DrawdownChart from './components/DrawdownChart';
import PLChart from './components/PLChart';
import SymbolPerformanceChart from './components/SymbolPerformanceChart';

const DashboardCharts = () => {
  const [filters, setFilters] = useState({ symbol: '', chartType: 'equity', fromTime: '', toTime: '' });
  const [symbols, setSymbols] = useState([]);

  // Recupera la lista dei simboli disponibili (puoi adattare la fonte dati)
  useEffect(() => {
    fetch('/api/live_status')
      .then(res => res.json())
      .then(data => {
        if (data && data.symbols) setSymbols(data.symbols);
      });
  }, []);

  // Costruisci i parametri per la query API
  const getQueryParams = () => {
    const params = [];
    if (filters.symbol) params.push(`symbol=${filters.symbol}`);
    if (filters.fromTime) params.push(`from_time=${new Date(filters.fromTime).getTime() / 1000}`);
    if (filters.toTime) params.push(`to_time=${new Date(filters.toTime).getTime() / 1000}`);
    return params.length ? `?${params.join('&')}` : '';
  };

  // Renderizza il grafico selezionato
  const renderChart = () => {
    const query = getQueryParams();
    switch (filters.chartType) {
      case 'equity':
        return <EquityChart query={query} />;
      case 'drawdown':
        return <DrawdownChart query={query} />;
      case 'pl':
        return <PLChart query={query} />;
      case 'performance':
        return <SymbolPerformanceChart query={query} />;
      default:
        return null;
    }
  };

  return (
    <div style={{ padding: '2rem' }}>
      <Filters symbols={symbols} onChange={setFilters} />
      {renderChart()}
    </div>
  );
};

export default DashboardCharts;
