@echo off
echo ========================================
echo  Voice Recording Setup
echo ========================================
echo.
echo This will install packages for voice recording.
echo The app works without these, but voice recording
echo requires them.
echo.
pause
echo.
echo Installing voice recording packages...
echo.

pip install streamlit-audio-recorder
if %errorlevel% neq 0 (
    echo.
    echo WARNING: Could not install streamlit-audio-recorder
    echo You can still use text input for sentiment analysis!
    echo.
)

pip install SpeechRecognition
if %errorlevel% neq 0 (
    echo.
    echo WARNING: Could not install SpeechRecognition
    echo.
)

pip install textblob
if %errorlevel% neq 0 (
    echo.
    echo WARNING: Could not install textblob
    echo.
)

echo.
echo Downloading TextBlob language data...
python -m textblob.download_corpora

echo.
echo ========================================
echo  Testing Installation
echo ========================================
echo.

python test_voice_recording.py

echo.
echo ========================================
echo  Setup Complete!
echo ========================================
echo.
echo To start the app:
echo   streamlit run enhanced_app.py
echo.
echo Then go to: Daily Mood Tracker -^> Voice Entry
echo.
echo NOTE: If audio recorder didn't install, you can
echo still use the text input - it works the same!
echo.
pause
