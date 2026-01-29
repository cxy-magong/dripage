# PowerShell script to start RPC server in background

$ErrorActionPreference = "Stop"

# Set directory
$projectDir = "G:\code\agent-use\dripage\worktrees\cdp-support"
Set-Location $projectDir

# Configure server
$host = "0.0.0.0"
$port = 9090

# Log file
$logFile = "rpc_server_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"

Write-Host "=============================================" -ForegroundColor Green
Write-Host "  Starting ChromeManager RPC Server" -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Green
Write-Host ""
Write-Host "Project: $projectDir" -ForegroundColor Cyan
Write-Host "Host: $host" -ForegroundColor Cyan
Write-Host "Port: $port" -ForegroundColor Cyan
Write-Host "Log: $logFile" -ForegroundColor Cyan
Write-Host ""

# Start server in background
$psiArgs = @{
    FilePath = "uv"
    ArgumentList = @("run", "services/chrome_rpc/start_server.py", "--host", $host, "--port", $port)
    RedirectStandardOutput = $logFile
    RedirectStandardError = $logFile
    WindowStyle = "Hidden"
    CreateNoWindow = $true
}

$process = Start-Process @psiArgs -PassThru

Write-Host "Server started!" -ForegroundColor Green
Write-Host "Process ID: $($process.Id)" -ForegroundColor Yellow
Write-Host ""
Write-Host "Waiting for server to initialize..." -ForegroundColor Yellow

# Wait a moment for server to start
Start-Sleep -Seconds 3

# Check if process is still running
if ($process.HasExited) {
    Write-Host "ERROR: Server process exited unexpectedly!" -ForegroundColor Red
    Write-Host "Check log file: $logFile" -ForegroundColor Red
    Get-Content $logFile -Tail 20
    exit 1
}

Write-Host "✅ Server is running!" -ForegroundColor Green
Write-Host ""
Write-Host "You can now run remote client test:" -ForegroundColor Cyan
Write-Host ""
Write-Host "  ssh sv-v2 `"cd ~/code/agent-use/dripage && uv run services/chrome_rpc/test_remote_client.py --host sv-v2.lan --port 9090`"" -ForegroundColor Yellow
Write-Host ""
Write-Host "Monitor server log:" -ForegroundColor Cyan
Write-Host "  Get-Content $logFile -Wait" -ForegroundColor Yellow
Write-Host ""
Write-Host "Stop server:" -ForegroundColor Cyan
Write-Host "  Stop-Process -Id $($process.Id) -Force" -ForegroundColor Yellow
Write-Host ""
