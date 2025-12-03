
$ScriptDir = Split-Path $MyInvocation.MyCommand.Path
Set-Location $ScriptDir
.\.venv\Scripts\Activate.ps1
uvicorn main:app --reload --host 0.0.0.0 --port 8000
