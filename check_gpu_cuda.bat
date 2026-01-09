@echo off
REM Batch script to run GPU/CUDA diagnostic
echo GPU and CUDA Diagnostic Tool
echo ============================================================
echo.

REM Try to find QGIS Python
set "QGIS_PYTHON="

if exist "C:\Program Files\QGIS 3.40.13\bin\python-qgis-ltr.bat" (
    set "QGIS_PYTHON=C:\Program Files\QGIS 3.40.13\bin\python-qgis-ltr.bat"
) else if exist "C:\OSGeo4W64\bin\python-qgis-ltr.bat" (
    set "QGIS_PYTHON=C:\OSGeo4W64\bin\python-qgis-ltr.bat"
) else (
    echo Searching for QGIS Python...
    for /d %%i in ("C:\Program Files\QGIS*") do (
        if exist "%%i\bin\python-qgis-ltr.bat" (
            set "QGIS_PYTHON=%%i\bin\python-qgis-ltr.bat"
            goto :found
        )
    )
    :found
)

if "%QGIS_PYTHON%"=="" (
    echo Using system Python...
    set "QGIS_PYTHON=python"
)

set "SCRIPT_DIR=%~dp0"
"%QGIS_PYTHON%" "%SCRIPT_DIR%check_gpu_cuda.py"

pause


