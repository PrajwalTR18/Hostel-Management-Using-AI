@echo off
echo ========================================================
echo  Starting SmartHostel AI Platform (Voice + AI Suite)
echo ========================================================
echo.
echo Launching Streamlit server on http://localhost:8501 ...
echo Opening your web browser automatically...
python -m streamlit run app.py --server.port 8501 --server.headless false --browser.gatherUsageStats false
pause
