@echo off
echo ======================================================================
echo Fixing Duplicate CuPy Installation
echo ======================================================================
echo.
echo Detected: Both cupy-cuda11x and cupy-cuda12x are installed
echo.
echo We will keep cupy-cuda12x (compatible with CUDA 13.0)
echo and remove cupy-cuda11x
echo.
pause

set QGIS_PYTHON="C:\Program Files\QGIS 3.40.13\bin\python-qgis-ltr.bat"

echo.
echo Step 1: Uninstalling cupy-cuda11x...
echo.
%QGIS_PYTHON% -m pip uninstall -y cupy-cuda11x

echo.
echo Step 2: Verifying cupy-cuda12x is still installed...
echo.
%QGIS_PYTHON% -m pip show cupy-cuda12x

echo.
echo ======================================================================
echo Done! Please restart QGIS to apply changes.
echo ======================================================================
echo.
pause

