import React, { useEffect, useState } from 'react';
import { getLiveStatus } from '../api';

export default function NotificationsLog() {
  const [log, setLog] = useState([]);
  useEffect(() => {
    getLiveStatus().then(status => setLog(status.notifications || []));
  }, []);
  if (!log.length) return <div>Nessuna notifica recente</div>;
  return (
    <div className="notifications-log">
      <h3>Log Eventi Recenti</h3>
      <ul>
        {log.map((n, i) => (
          <li key={i}>{n.timestamp ? new Date(n.timestamp * 1000).toLocaleString() + ': ' : ''}{n.message}</li>
        ))}
      </ul>
    </div>
  );
}
