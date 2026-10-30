@echo off
echo ========================================================
echo  Starting SmartHostel AI Platform (Voice + AI Suite)
echo ========================================================
echo.
echo Opening browser at http://localhost:8501 ...
start http://localhost:8501
python -m streamlit run app.py --server.port 8501 --server.headless false --browser.gatherUsageStats false
pause
