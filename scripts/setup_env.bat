@echo off
setlocal ENABLEDELAYEDEXPANSION

REM =========================
REM CONFIG
REM =========================
set ENV_NAME=data_env
set PYTHON_VERSION=3.11
set REQUIREMENTS=requirements.txt
set TEST_SCRIPT=broken_env.py

echo =========================
echo   SETUP START
echo =========================

REM =========================
REM 1. Locate conda
REM =========================

set CONDA_EXE=

where conda >nul 2>&1
if %errorlevel%==0 (
    for /f "delims=" %%i in ('where conda') do (
        set CONDA_EXE=%%i
        goto :conda_found
    )
)

REM Try default locations
if exist "%USERPROFILE%\anaconda3\condabin\conda.bat" (
    set CONDA_EXE=%USERPROFILE%\anaconda3\condabin\conda.bat
    goto :conda_found
)

if exist "C:\ProgramData\anaconda3\condabin\conda.bat" (
    set CONDA_EXE=C:\ProgramData\anaconda3\condabin\conda.bat
    goto :conda_found
)

echo [ERROR] Conda not found.
goto :error

:conda_found
echo Using conda: %CONDA_EXE%

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
    conda run -n %ENV_NAME% python -m pip install -r %REQUIREMENTS%
    if %errorlevel% neq 0 goto :error
) else (
    echo No requirements.txt found. Skipping dependency installation.
)

REM =========================
REM 4. Smoke test
REM =========================

echo Running smoke test...
conda run -n %ENV_NAME% python %TEST_SCRIPT%
if %errorlevel% neq 0 goto :error

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

