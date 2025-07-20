#!/bin/bash
# KLMNR AUTO-SYNC SCRIPT (per server Linux/WSL)
# Monitora GitHub e aggiorna automaticamente il server

REPO_DIR="/path/to/KLMNR_Phoenix_Quantum"
CHECK_INTERVAL=300  # 5 minuti

echo "🔄 KLMNR Auto-Sync avviato..."
echo "📁 Directory: $REPO_DIR"
echo "⏱️  Intervallo: ${CHECK_INTERVAL}s"

cd "$REPO_DIR" || exit 1

while true; do
    echo "$(date): 🔍 Controllo aggiornamenti GitHub..."
    
    # Fetch remote changes
    git fetch origin main
    
    # Check if updates available
    LOCAL=$(git rev-parse HEAD)
    REMOTE=$(git rev-parse origin/main)
    
    if [ "$LOCAL" != "$REMOTE" ]; then
        echo "$(date): 📥 Nuovi aggiornamenti trovati!"
        
        # Stop trading system
        echo "$(date): ⏸️  Fermando sistema trading..."
        pkill -f "python.*quantum_main"
        pkill -f "terminal64"
        
        # Pull changes
        echo "$(date): 📥 Pull modifiche..."
        git pull origin main
        
        # Restart trading system  
        echo "$(date): 🚀 Riavvio sistema..."
        nohup python quantum_main_refactored.py &
        
        echo "$(date): ✅ Aggiornamento completato!"
        
        # Send notification (optional)
        # curl -X POST "https://api.telegram.org/bot<token>/sendMessage" \
        #      -d "chat_id=<chat_id>&text=KLMNR Server aggiornato!"
        
    else
        echo "$(date): ✅ Sistema aggiornato"
    fi
    
    sleep $CHECK_INTERVAL
done
