@echo off
REM Daily job update batch script for Windows

echo 🚀 Starting daily LinkedIn job update...
echo 📅 %date% %time%

REM Change to script directory
cd /d "%~dp0"

REM Activate virtual environment if it exists
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
    echo ✅ Activated virtual environment
)

REM Run the daily update script
python daily_update.py

REM Add, commit, and push to git
echo 🔄 Updating git repository...
git add jobs_database.json
git commit -m "Daily job update - %date%"
git push

echo ✅ Daily update completed!
echo 📊 Check your Railway app for updated jobs

pause