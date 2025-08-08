@echo off
REM Run Flask app in background using start
start "Flask Server" cmd /k "python app.py"

REM Wait 5 seconds for the Flask server to fully start
timeout /t 5 >nul

:loop
echo Taking screenshot...
python capture.py

REM Wait 15 seconds before next capture
timeout /t 15 >nul
goto loop
