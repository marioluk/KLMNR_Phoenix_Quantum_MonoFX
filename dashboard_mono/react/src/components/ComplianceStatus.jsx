import React, { useEffect, useState } from 'react';
import { getLiveStatus } from '../api';

export default function ComplianceStatus() {
  const [compliance, setCompliance] = useState(null);
  useEffect(() => {
    getLiveStatus().then(status => setCompliance(status.compliance_status));
  }, []);
  if (!compliance) return <div>Caricamento stato compliance...</div>;
  return (
    <div className="compliance-status">
      <h3>Stato Challenge & Compliance</h3>
      <ul>
        <li>Target raggiunto: {compliance.target_reached ? '✅' : '❌'}</li>
        <li>Drawdown: {compliance.drawdown}</li>
        <li>Limiti: {compliance.limits}</li>
        <li>Warning: {compliance.warning ? '⚠️' : 'OK'}</li>
      </ul>
    </div>
  );
}
