# =================================================================
# AUTO START LEGACY - PowerShell Script per Task Scheduler
# Sistema legacy con restart automatico e monitoraggio
# =================================================================

param(
    [switch]$NoRestart,
    [int]$MaxRestarts = 5,
    [int]$RestartDelay = 30
)

# Setup logging
$LogDir = "C:\KLMNR_Projects\KLMNR_Phoenix_Quantum\legacy_system\logs"
$LogFile = Join-Path $LogDir "auto_start_$(Get-Date -Format 'yyyyMMdd').log"

function Write-Log {
    param($Message, $Level = "INFO")
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $LogEntry = "[$Timestamp] [$Level] $Message"
    Write-Host $LogEntry
    Add-Content -Path $LogFile -Value $LogEntry -Encoding UTF8
}

function Test-NetworkConnection {
    try {
        $ping = Test-Connection -ComputerName "8.8.8.8" -Count 1 -Quiet
        return $ping
    }
    catch {
        return $false
    }
}

function Start-LegacySystem {
    $WorkDir = "C:\KLMNR_Projects\KLMNR_Phoenix_Quantum\legacy_system"
    
    Write-Log "Cambio directory a: $WorkDir"
    Set-Location $WorkDir
    
    # Verifica file principali
    if (!(Test-Path "PRO-THE5ERS-QM-PHOENIX-GITCOP.py")) {
        Write-Log "ERRORE: File principale non trovato!" "ERROR"
        return $false
    }
    
    if (!(Test-Path "config/config_autonomous_high_stakes_production_ready.json")) {
        Write-Log "ERRORE: File configurazione non trovato!" "ERROR"
        return $false
    }
    
    Write-Log "File sistema verificati"
    
    # Attendi connessione di rete
    Write-Log "Verifica connessione di rete..."
    $NetworkRetries = 0
    while (!(Test-NetworkConnection) -and $NetworkRetries -lt 6) {
        $NetworkRetries++
        Write-Log "Connessione non disponibile, tentativo $NetworkRetries/6" "WARNING"
        Start-Sleep 30
    }
    
    if (!(Test-NetworkConnection)) {
        Write-Log "Connessione di rete non disponibile dopo 3 minuti" "ERROR"
        return $false
    }
    
    Write-Log "Connessione di rete verificata"
    
    # Avvia sistema legacy
    Write-Log "=== AVVIO SISTEMA LEGACY ==="
    
    try {
        $Process = Start-Process -FilePath "python" -ArgumentList "PRO-THE5ERS-QM-PHOENIX-GITCOP.py" -NoNewWindow -PassThru -Wait
        
        Write-Log "Sistema legacy terminato con exit code: $($Process.ExitCode)"
        
        if ($Process.ExitCode -eq 0) {
            Write-Log "Sistema terminato normalmente" "SUCCESS"
            return $true
        }
        else {
            Write-Log "Sistema terminato con errore" "ERROR"
            return $false
        }
    }
    catch {
        Write-Log "Errore durante l'esecuzione: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

# Main execution
Write-Log "=========================================="
Write-Log "AVVIO AUTOMATICO SISTEMA LEGACY"
Write-Log "Max Restarts: $MaxRestarts"
Write-Log "Restart Delay: $RestartDelay secondi"
Write-Log "=========================================="

$RestartCount = 0

do {
    if ($RestartCount -gt 0) {
        Write-Log "=== RESTART $RestartCount/$MaxRestarts ==="
        Write-Log "Attesa $RestartDelay secondi prima del restart..."
        Start-Sleep $RestartDelay
    }
    
    $Success = Start-LegacySystem
    
    if ($Success) {
        Write-Log "Sistema completato con successo"
        break
    }
    else {
        $RestartCount++
        if ($NoRestart) {
            Write-Log "Restart disabilitato, uscita" "WARNING"
            break
        }
        
        if ($RestartCount -ge $MaxRestarts) {
            Write-Log "Raggiunto limite massimo di restart ($MaxRestarts)" "ERROR"
            break
        }
        
        Write-Log "Sistema fallito, scheduling restart..." "WARNING"
    }
    
} while ($RestartCount -lt $MaxRestarts)

Write-Log "=========================================="
Write-Log "FINE ESECUZIONE - Restarts: $RestartCount"
Write-Log "=========================================="
