# start_all.ps1

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition

# Activate venv - full path
$venvActivate = Join-Path $scriptDir ".venv\Scripts\Activate.ps1"
Write-Host "Activating virtual environment: $venvActivate"
& $venvActivate

# Start AS/RS integration
Start-Process powershell -ArgumentList '-NoExit','-Command', "cd `"$scriptDir\AS_RS_System\asrs_integration`"; python main_service.py"

# Start backend on port 4000
Start-Process powershell -ArgumentList '-NoExit','-Command', "cd `"$scriptDir\AS_RS_System\inventory-system\inventory-system\backend`"; npm run dev"

# Start frontend
Start-Process powershell -ArgumentList '-NoExit','-Command', "cd `"$scriptDir\AS_RS_System\inventory-system\inventory-system\frontend`"; npm run dev"

Write-Host "All services started."
Write-Host "Frontend likely at http://localhost:3000"
Write-Host "Backend API at http://localhost:4000"
