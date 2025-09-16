# start_all.ps1

# 1) Start AS/RS Integration Service
Write-Host "Starting AS/RS Integration Service..."
Push-Location .\AS_RS_System\asrs_integration
# Activate virtualenv
& "..\..\.venv\Scripts\Activate.ps1"
Start-Process -NoNewWindow -FilePath python -ArgumentList main_service.py
Pop-Location

# 2) Start Backend API
Write-Host "Starting Backend API..."
Push-Location .\AS_RS_System\inventory-system\backend
npm install
Start-Process -NoNewWindow -FilePath npm -ArgumentList 'run','dev'
Pop-Location

# 3) Start Frontend UI
Write-Host "Starting Frontend UI..."
Push-Location .\AS_RS_System\inventory-system\frontend
npm install
Start-Process -NoNewWindow -FilePath npm -ArgumentList 'run','dev'
Pop-Location

Write-Host "All services started. Frontend: http://localhost:5173  Backend: http://localhost:4000/api"
