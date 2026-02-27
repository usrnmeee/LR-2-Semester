@echo off
setlocal ENABLEDELAYEDEXPANSION

REM =========================
REM CONFIG
REM =========================
set ENV_NAME=data_env
set PYTHON_VERSION=3.11
set REQUIREMENTS=../requirements.txt
set TEST_SCRIPT=../broken_env.py

echo =========================
echo       SETUP START
echo =========================
echo.

REM =========================
REM 1. Find conda
REM =========================

where conda >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Conda not found in PATH.
    goto :error
)

for /f "delims=" %%i in ('where conda') do (
    set CONDA_PATH=%%i
    goto :found_conda
)

:found_conda
echo Found conda: %CONDA_PATH%

REM =========================
REM 2. Check if env exists
REM =========================

conda env list | findstr /C:"%ENV_NAME%" >nul
if %errorlevel% neq 0 (
    echo Environment %ENV_NAME% not found. Creating...
    conda create -n %ENV_NAME% python=%PYTHON_VERSION% -y
    if %errorlevel% neq 0 goto :error
) else (
    echo Environment %ENV_NAME% already exists.
)

REM =========================
REM 3. Install dependencies
REM =========================

if exist %REQUIREMENTS% (
    echo Installing dependencies...
    call conda run -n %ENV_NAME% python -m pip install -r %REQUIREMENTS%
    if %errorlevel% neq 0 goto :error
) else (
    echo No requirements.txt found. Skipping dependency installation.
)

REM =========================
REM 4. Smoke test
REM =========================

echo Running smoke test...
call conda activate %ENV_NAME%
call python %TEST_SCRIPT%
call conda deactivate
if %errorlevel% neq 0 goto :error

echo.
echo =========================
echo        [OK]
echo =========================
goto :end

:error
echo =========================
echo       [ERROR]
echo =========================

:end
echo.
echo Press any key to exit...
pause >nul
exit /b