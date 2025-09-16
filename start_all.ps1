# Start ASRS Integration Service in new window
Start-Process powershell -ArgumentList '-NoExit', '-Command', "cd .\AS_RS_System\asrs_integration; .\.venv\Scripts\Activate.ps1; python main_service.py"

# Start Backend API in new window
Start-Process powershell -ArgumentList '-NoExit', '-Command', "cd .\AS_RS_System\inventory-system\inventory-system\backend; npm run dev"

# Start Frontend UI in new window
Start-Process powershell -ArgumentList '-NoExit', '-Command', "cd .\AS_RS_System\inventory-system\inventory-system\frontend; npm run dev"

Write-Host "All services launched in new PowerShell windows."
Write-Host "Frontend: http://localhost:5173"
Write-Host "Backend: http://localhost:4000/api"
