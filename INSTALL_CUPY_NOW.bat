@echo off
echo ======================================================================
echo Installing CuPy for DEM Downscaling Plugin
echo ======================================================================
echo.

REM Try to find QGIS Python executable
set QGIS_PYTHON="C:\Program Files\QGIS 3.40.13\bin\python-qgis-ltr.bat"

if not exist %QGIS_PYTHON% (
    echo [ERROR] QGIS Python not found at: %QGIS_PYTHON%
    echo.
    echo Please update the path in this batch file to match your QGIS installation.
    echo Common locations:
    echo   - C:\Program Files\QGIS 3.40.13\bin\python-qgis-ltr.bat
    echo   - C:\Program Files\QGIS 3.36.0\bin\python-qgis-ltr.bat
    echo   - C:\OSGeo4W64\bin\python-qgis-ltr.bat
    echo.
    pause
    exit /b 1
)

echo Step 1: Checking CUDA Toolkit version...
echo.
%QGIS_PYTHON% -c "import os; path='C:\\Program Files\\NVIDIA GPU Computing Toolkit\\CUDA'; print('Checking:', path); versions=[d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d)) and d.startswith('v')]; print('Found versions:', versions) if versions else print('CUDA Toolkit not found')"

echo.
echo ======================================================================
echo Step 2: Installing CuPy for CUDA 12.x
echo ======================================================================
echo.
echo Note: You have CUDA Toolkit 13.0 installed.
echo CuPy may not have official support for CUDA 13.0 yet.
echo We will try cupy-cuda12x (compatible with CUDA 12.x and may work with 13.0 driver)
echo.
echo This may take 5-15 minutes and download ~500 MB...
echo.

%QGIS_PYTHON% -m pip install cupy-cuda12x

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ======================================================================
    echo [SUCCESS] CuPy installed successfully!
    echo ======================================================================
    echo.
    echo Next steps:
    echo 1. Close this window
    echo 2. Restart QGIS completely
    echo 3. Run check_gpu_cuda.py to verify installation
    echo.
) else (
    echo.
    echo ======================================================================
    echo [ERROR] CuPy installation failed
    echo ======================================================================
    echo.
    echo Possible reasons:
    echo 1. Network connection issues
    echo 2. CUDA 13.0 not yet supported by CuPy
    echo 3. Missing dependencies
    echo.
    echo Alternative: Use CPU processing with SciPy instead
    echo   Run: %QGIS_PYTHON% -m pip install scipy
    echo.
)

pause

