@echo off
echo Checking for Python...

:: Try to find Python using 'py' launcher (recommended way on Windows)
py --version >nul 2>&1
if %ERRORLEVEL% == 0 (
    echo Python found using 'py' launcher.
    set PYTHON_CMD=py
    goto :python_found
)

:: Try to find Python using 'python' command
python --version >nul 2>&1
if %ERRORLEVEL% == 0 (
    echo Python found using 'python' command.
    set PYTHON_CMD=python
    goto :python_found
)

:: Try to find Python using 'python3' command (less common on Windows)
python3 --version >nul 2>&1
if %ERRORLEVEL% == 0 (
    echo Python found using 'python3' command.
    set PYTHON_CMD=python3
    goto :python_found
)

echo ERROR: Python could not be found. Please make sure Python is installed and added to your PATH.
echo You can download Python from https://www.python.org/downloads/
exit /b 1

:python_found
echo Checking virtual environment...

if defined VIRTUAL_ENV (
    echo Virtual environment detected.
) else if defined CONDA_PREFIX (
    echo Conda environment detected.
) else (
    echo No virtual environment detected.
    echo.
    echo === This script is going to install the project in the system python environment ===
    set /p RESPONSE="Proceed? [y/N]: "
    if /i not "%RESPONSE%"=="y" (
        echo See https://lincc-ppt.readthedocs.io/ for details.
        echo Exiting.
        exit /b 1
    )
)

echo Checking pip version...
for /f "tokens=2" %%i in ('%PYTHON_CMD% -m pip --version ^| findstr /r "[0-9]*\.[0-9]*"') do set PIPVER=%%i
for /f "tokens=1 delims=." %%a in ("%PIPVER%") do set PIPVERMAJOR=%%a

if %PIPVERMAJOR% LSS 22 (
    echo Insufficient version of pip found. Requires at least version 22.
    echo See https://lincc-ppt.readthedocs.io/ for details.
    exit /b 1
)

echo Installing package and runtime dependencies in local environment...
%PYTHON_CMD% -m pip install -e . 

echo Installing developer dependencies in local environment...
%PYTHON_CMD% -m pip install -e .[dev]

if exist docs\requirements.txt (
    echo Installing documentation dependencies...
    %PYTHON_CMD% -m pip install -r docs\requirements.txt
)

echo Installing pre-commit...
%PYTHON_CMD% -m pip install pre-commit
%PYTHON_CMD% -m pre-commit install

echo Setup completed successfully!