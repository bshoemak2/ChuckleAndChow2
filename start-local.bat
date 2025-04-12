@ECHO off
ECHO Starting Flask backend...
if exist .env (
    for /f "tokens=1,2 delims==" %%a in (.env) do (
        set %%a=%%b
        echo Setting %%a=%%b
    )
)
start cmd /k "python app.py & echo Waiting for Flask to start... & timeout /t 5 & echo Flask should be running at http://127.0.0.1:5000"
ECHO Building and serving Expo web app locally in development mode...
npx expo start --web