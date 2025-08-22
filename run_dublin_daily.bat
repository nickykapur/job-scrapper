@echo off
REM Daily Dublin job update batch script for Windows

echo 🚀 Starting Daily Dublin Job Search (Last 24 Hours)
echo 📅 %date% %time%
echo 🎯 Target: Dublin, Ireland Software Jobs

REM Change to script directory
cd /d "%~dp0"

REM Activate virtual environment if it exists
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
    echo ✅ Activated virtual environment
)

REM Run the Dublin-specific daily update script
echo 🔍 Running Dublin job search...
python daily_dublin_update.py

if %ERRORLEVEL% NEQ 0 (
    echo ❌ Dublin job search failed
    pause
    exit /b 1
)

REM Add, commit, and push to git
echo 🔄 Updating git repository...
git add jobs_database.json

REM Check if there are changes to commit
git diff --cached --quiet
if %ERRORLEVEL% NEQ 0 (
    git commit -m "🏙️ Dublin 24h job update - %date%"
    git push
    echo ✅ Changes pushed to git - Railway will auto-deploy!
) else (
    echo ℹ️ No changes detected - database unchanged
)

echo 📊 Check your Railway app at: https://yourapp.railway.app
echo 🎉 Daily Dublin update completed!

pause