@echo off
echo Starting Tengen.ai Application...
echo.

echo Starting Backend Server...
start "Tengen Backend" cmd /k "cd backend && python app.py"

echo Waiting for backend to start...
timeout /t 5 /nobreak > nul

echo Starting Frontend Server...
start "Tengen Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo ========================================
echo Tengen.ai is starting up!
echo ========================================
echo Backend API: http://localhost:8000
echo Frontend UI: http://localhost:3000
echo API Docs: http://localhost:8000/docs
echo ========================================
echo.
echo Press any key to close this window...
pause > nul