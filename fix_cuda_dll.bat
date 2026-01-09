@echo off
REM Batch script to run CUDA DLL fix utility
REM This script finds the QGIS Python and runs the fix script

echo CUDA DLL Fix Utility for QGIS DEM Downscaling Plugin
echo ============================================================
echo.

REM Try to find QGIS Python
REM Common QGIS installation paths
set "QGIS_PYTHON="

if exist "C:\Program Files\QGIS 3.40.13\bin\python-qgis-ltr.bat" (
    set "QGIS_PYTHON=C:\Program Files\QGIS 3.40.13\bin\python-qgis-ltr.bat"
) else if exist "C:\OSGeo4W64\bin\python-qgis-ltr.bat" (
    set "QGIS_PYTHON=C:\OSGeo4W64\bin\python-qgis-ltr.bat"
) else (
    echo Searching for QGIS Python...
    REM Try to find python-qgis*.bat in Program Files
    for /d %%i in ("C:\Program Files\QGIS*") do (
        if exist "%%i\bin\python-qgis-ltr.bat" (
            set "QGIS_PYTHON=%%i\bin\python-qgis-ltr.bat"
            goto :found
        )
    )
    :found
)

if "%QGIS_PYTHON%"=="" (
    echo ERROR: Could not find QGIS Python executable.
    echo.
    echo Please run this script manually with:
    echo   "C:\Program Files\QGIS 3.40.13\bin\python-qgis-ltr.bat" fix_cuda_dll.py
    echo.
    echo Replace the path with your actual QGIS Python path.
    echo.
    pause
    exit /b 1
)

echo Using QGIS Python: %QGIS_PYTHON%
echo.

REM Get the directory where this batch file is located
set "SCRIPT_DIR=%~dp0"

REM Run the fix script
"%QGIS_PYTHON%" "%SCRIPT_DIR%fix_cuda_dll.py"

pause



