@echo off
setlocal

set "PROJECT_ROOT=%~dp0"
set "BACKEND_DIR=%PROJECT_ROOT%backend"
set "VENV_DIR=%BACKEND_DIR%\.venv"
set "PYTHON=python"

where python >nul 2>nul
if errorlevel 1 (
  where py >nul 2>nul
  if errorlevel 1 (
    echo Errore: Python non trovato. Installa Python 3.11+ e riprova.
    exit /b 1
  )
  set "PYTHON=py -3"
)

cd /d "%BACKEND_DIR%"
if errorlevel 1 exit /b 1

if not exist "%VENV_DIR%\Scripts\python.exe" (
  echo Creo virtual environment...
  %PYTHON% -m venv "%VENV_DIR%"
  if errorlevel 1 exit /b 1
)

set "VENV_PYTHON=%VENV_DIR%\Scripts\python.exe"

echo Installo/aggiorno dipendenze...
"%VENV_PYTHON%" -m pip install -r requirements.txt
if errorlevel 1 exit /b 1

if not exist ".env" (
  echo Creo backend\.env da backend\.env.example...
  copy ".env.example" ".env" >nul
  if errorlevel 1 exit /b 1
)

echo.
echo Revelio avviato su http://127.0.0.1:8000/
echo API docs: http://127.0.0.1:8000/docs
echo.

"%VENV_PYTHON%" -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
