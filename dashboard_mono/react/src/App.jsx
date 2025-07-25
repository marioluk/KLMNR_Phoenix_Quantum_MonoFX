import LiveStatus from './components/LiveStatus';
import PositionsTable from './components/PositionsTable';
import TradeHistory from './components/TradeHistory';
import QuantumSignals from './components/QuantumSignals';
import PerformanceMetrics from './components/PerformanceMetrics';
import DashboardCharts from './DashboardCharts';
import ComplianceStatus from './components/ComplianceStatus';
import NotificationsLog from './components/NotificationsLog';
import OrderManager from './components/OrderManager';

function App() {
  return (
    <div style={{ padding: 20 }}>
      <h1>Dashboard Quantistica</h1>
      <h2>Live Status & Tick</h2>
      <LiveStatus />
      <h2>Posizioni Aperte</h2>
      <PositionsTable />
      <h2>Storico Operazioni</h2>
      <TradeHistory />
      <h2>Segnali Quantum</h2>
      <QuantumSignals />
      <h2>Metriche di Performance</h2>
      <PerformanceMetrics />

      <h2>Grafici Avanzati</h2>
      <DashboardCharts />
      <h2>Stato Compliance & Obiettivi</h2>
      <ComplianceStatus />
      <h2>Log Eventi Recenti</h2>
      <NotificationsLog />
      <h2>Gestione Ordini Manuali</h2>
      <OrderManager />
    </div>
  );
}

export default App;
