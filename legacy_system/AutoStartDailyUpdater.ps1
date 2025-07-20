# ==============================================================================
# AUTO START DAILY CONFIG UPDATER - PowerShell Script
# Esecuzione automatica daily_config_updater.py alle 06:00
# ==============================================================================

param(
    [string]$LogPath = "",
    [int]$MaxRetries = 3,
    [int]$RetryDelaySeconds = 60
)

# Configurazione paths
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$LegacyDir = $ScriptDir
$BacktestDir = Join-Path $LegacyDir "backtest_legacy"
$LogsDir = Join-Path $LegacyDir "logs"
$UpdaterScript = Join-Path $BacktestDir "daily_config_updater.py"
$UpdaterBat = Join-Path $BacktestDir "daily_config_updater.bat"

# Log file per auto-start (separato dai log del sistema)
if ($LogPath -eq "") {
    $LogPath = Join-Path $LogsDir "auto_start_daily_updater_$(Get-Date -Format 'yyyyMMdd').log"
}

# Funzione di logging
function Write-AutoLog {
    param([string]$Message, [string]$Level = "INFO")
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $LogEntry = "[$Timestamp] [$Level] $Message"
    Write-Host $LogEntry
    Add-Content -Path $LogPath -Value $LogEntry -Encoding UTF8
}

# Funzione per test connettività
function Test-InternetConnection {
    try {
        $Result = Test-NetConnection -ComputerName "8.8.8.8" -Port 53 -InformationLevel Quiet -WarningAction SilentlyContinue
        return $Result
    } catch {
        return $false
    }
}

# Funzione per verifica ambiente Python
function Test-PythonEnvironment {
    param([string]$WorkingDir)
    
    Push-Location $WorkingDir
    try {
        # Test se il file principale esiste
        if (-not (Test-Path $UpdaterScript)) {
            Write-AutoLog "File daily_config_updater.py non trovato: $UpdaterScript" "ERROR"
            return $false
        }
        
        # Test import Python (rapido)
        $TestCmd = "python -c `"import sys, os; print('Python OK')`""
        $TestResult = Invoke-Expression $TestCmd 2>$null
        
        if ($TestResult -like "*Python OK*") {
            Write-AutoLog "Ambiente Python verificato con successo" "INFO"
            return $true
        } else {
            Write-AutoLog "Ambiente Python non funzionante" "ERROR"
            return $false
        }
    } catch {
        Write-AutoLog "Errore verifica ambiente Python: $($_.Exception.Message)" "ERROR"
        return $false
    } finally {
        Pop-Location
    }
}

# Inizio script
Write-AutoLog "==================================================================================="
Write-AutoLog "KLMNR DAILY CONFIG UPDATER - AUTO START SYSTEM"
Write-AutoLog "==================================================================================="
Write-AutoLog "Avvio: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
Write-AutoLog "Script: $UpdaterScript"
Write-AutoLog "Working Dir: $BacktestDir"
Write-AutoLog "Log File: $LogPath"

# Crea directory logs se non esiste
if (-not (Test-Path $LogsDir)) {
    New-Item -Path $LogsDir -ItemType Directory -Force | Out-Null
    Write-AutoLog "Directory logs creata: $LogsDir" "INFO"
}

# Verifica connettività internet
Write-AutoLog "Verifica connettività internet..." "INFO"
if (-not (Test-InternetConnection)) {
    Write-AutoLog "ATTENZIONE: Connessione internet non disponibile" "WARNING"
    Write-AutoLog "Il daily config updater potrebbe non funzionare correttamente" "WARNING"
} else {
    Write-AutoLog "Connessione internet verificata" "INFO"
}

# Verifica ambiente Python
Write-AutoLog "Verifica ambiente Python..." "INFO"
if (-not (Test-PythonEnvironment -WorkingDir $BacktestDir)) {
    Write-AutoLog "ERRORE: Ambiente Python non configurato correttamente" "ERROR"
    Write-AutoLog "Auto-start terminato con errore" "ERROR"
    exit 1
}

# Loop di retry per l'esecuzione
$RetryCount = 0
$Success = $false

while ($RetryCount -lt $MaxRetries -and -not $Success) {
    $RetryCount++
    
    if ($RetryCount -gt 1) {
        Write-AutoLog "Tentativo #$RetryCount di $MaxRetries..." "INFO"
    }
    
    try {
        # Cambia directory di lavoro
        Set-Location $BacktestDir
        Write-AutoLog "Directory cambiata: $BacktestDir" "INFO"
        
        # Esegui daily config updater
        Write-AutoLog "Avvio daily config updater..." "INFO"
        
        # Usa il BAT wrapper se esiste, altrimenti Python diretto
        if (Test-Path $UpdaterBat) {
            Write-AutoLog "Esecuzione via BAT wrapper: daily_config_updater.bat" "INFO"
            $Process = Start-Process -FilePath "cmd.exe" -ArgumentList "/c", "daily_config_updater.bat" -Wait -PassThru -NoNewWindow
        } else {
            Write-AutoLog "Esecuzione diretta Python: daily_config_updater.py" "INFO"
            $Process = Start-Process -FilePath "python" -ArgumentList "daily_config_updater.py", "--days", "30" -Wait -PassThru -NoNewWindow
        }
        
        # Controlla risultato
        $ExitCode = $Process.ExitCode
        
        if ($ExitCode -eq 0) {
            Write-AutoLog "Daily config updater completato con successo!" "INFO"
            Write-AutoLog "Exit code: $ExitCode" "INFO"
            $Success = $true
        } else {
            Write-AutoLog "Daily config updater terminato con errori (Exit code: $ExitCode)" "ERROR"
            
            if ($RetryCount -lt $MaxRetries) {
                Write-AutoLog "Retry in $RetryDelaySeconds secondi..." "INFO"
                Start-Sleep -Seconds $RetryDelaySeconds
            }
        }
        
    } catch {
        Write-AutoLog "Errore durante esecuzione: $($_.Exception.Message)" "ERROR"
        
        if ($RetryCount -lt $MaxRetries) {
            Write-AutoLog "Retry in $RetryDelaySeconds secondi..." "INFO"
            Start-Sleep -Seconds $RetryDelaySeconds
        }
    }
}

# Risultato finale
if ($Success) {
    Write-AutoLog "==================================================================================="
    Write-AutoLog "DAILY CONFIG UPDATER AUTO-START COMPLETATO CON SUCCESSO"
    Write-AutoLog "Configurazioni ottimali generate e convertite per produzione"
    Write-AutoLog "Sistema legacy avrà le nuove configurazioni al prossimo riavvio"
    Write-AutoLog "==================================================================================="
    exit 0
} else {
    Write-AutoLog "==================================================================================="
    Write-AutoLog "DAILY CONFIG UPDATER AUTO-START FALLITO"
    Write-AutoLog "Falliti tutti i $MaxRetries tentativi di esecuzione"
    Write-AutoLog "Verificare logs del daily config updater per dettagli"
    Write-AutoLog "==================================================================================="
    exit 1
}
