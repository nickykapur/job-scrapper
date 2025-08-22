@echo off
REM Setup Windows Task Scheduler for Daily Job Updates

echo 🚀 Setting up daily LinkedIn job scraping task...

REM Create the daily task
schtasks /create /sc daily /tn "LinkedIn Job Scraper" /tr "%cd%\run_daily_update.bat" /st 09:00

echo ✅ Task created! Daily job scraping will run at 9:00 AM
echo 🔧 You can modify the schedule in Task Scheduler if needed

pause