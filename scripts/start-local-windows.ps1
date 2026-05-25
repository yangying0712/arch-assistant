param(
    [string]$Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
)

$ErrorActionPreference = "Stop"

function Import-DotEnv {
    param([string]$Path)
    if (-not (Test-Path -LiteralPath $Path)) {
        return
    }

    Get-Content -LiteralPath $Path | ForEach-Object {
        $line = $_.Trim()
        if (-not $line -or $line.StartsWith("#") -or -not $line.Contains("=")) {
            return
        }
        $name, $value = $line.Split("=", 2)
        $name = $name.Trim()
        $value = $value.Trim().Trim('"').Trim("'")
        if ($name) {
            [Environment]::SetEnvironmentVariable($name, $value, "Process")
        }
    }
}

function Start-ServiceProcess {
    param(
        [string]$Name,
        [string]$WorkingDirectory,
        [int]$Port,
        [string]$Module
    )

    $outLogPath = Join-Path $Root "logs\$Name.out.log"
    $errLogPath = Join-Path $Root "logs\$Name.err.log"
    $python = Join-Path $Root ".venv-win\Scripts\python.exe"

    $process = Start-Process -FilePath $python `
        -ArgumentList "-m", "uvicorn", $Module, "--host", "127.0.0.1", "--port", "$Port" `
        -WorkingDirectory $WorkingDirectory `
        -RedirectStandardOutput $outLogPath `
        -RedirectStandardError $errLogPath `
        -WindowStyle Hidden `
        -PassThru

    [PSCustomObject]@{
        Name = $Name
        Port = $Port
        Pid  = $process.Id
        Out  = $outLogPath
        Err  = $errLogPath
    }
}

$venvPython = Join-Path $Root ".venv-win\Scripts\python.exe"
if (-not (Test-Path -LiteralPath $venvPython)) {
    throw "Missing .venv-win. Create it first with: python -m venv .venv-win"
}

New-Item -ItemType Directory -Force -Path (Join-Path $Root "logs") | Out-Null
Import-DotEnv -Path (Join-Path $Root ".env")

$env:LLM_ROUTER_HOST = "http://127.0.0.1:8002"
$env:AGENT_RUNTIME_HOST = "http://127.0.0.1:8003"
$env:ORCHESTRATION_HOST = "http://127.0.0.1:8001"
$env:FRONTEND_DIST = Join-Path $Root "frontend\dist"

$services = @(
    @{ Name = "llm-router"; WorkingDirectory = Join-Path $Root "apps\llm-router"; Port = 8002; Module = "llm_router.main:app" },
    @{ Name = "agent-runtime"; WorkingDirectory = Join-Path $Root "apps\agent-runtime"; Port = 8003; Module = "agent_runtime.main:app" },
    @{ Name = "orchestration-engine"; WorkingDirectory = Join-Path $Root "apps\orchestration-engine"; Port = 8001; Module = "orchestration_engine.main:app" },
    @{ Name = "api-gateway"; WorkingDirectory = Join-Path $Root "apps\api-gateway"; Port = 3000; Module = "api_gateway.main:app" }
)

$started = foreach ($service in $services) {
    Start-ServiceProcess @service
    Start-Sleep -Milliseconds 500
}

$started | Format-Table -AutoSize
Write-Host ""
Write-Host "Open http://127.0.0.1:3000/ after health checks pass."
Write-Host "Logs are in: $(Join-Path $Root "logs")"
