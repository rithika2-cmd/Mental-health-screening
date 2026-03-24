@echo off
echo ========================================
echo  Relaxation Audio Setup
echo ========================================
echo.
echo This will download 9 relaxation audio files
echo Total size: approximately 50-100 MB
echo.
pause
echo.
echo Downloading audio files...
echo.

python download_audio.py

echo.
echo ========================================
echo  Setup Complete!
echo ========================================
echo.
echo Audio files are in the 'audio' folder
echo.
echo To use them:
echo   streamlit run enhanced_app.py
echo.
echo Then go to: Stress Relief Games -^> Relaxation Sounds
echo.
pause
