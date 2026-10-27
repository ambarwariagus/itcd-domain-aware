@echo off
REM Quick Test Script for ITCD Domain-Aware (Windows)
REM This script performs basic validation without running the full pipeline

echo ==========================================
echo ITCD Domain-Aware - Quick Validation
echo ==========================================
echo.

REM Check Python version
echo [1/6] Checking Python version...
python --version
echo.

REM Check project structure
echo [2/6] Validating project structure...
if exist "src" (
    if exist "data" (
        if exist "models" (
            if exist "output" (
                echo [OK] Directory structure OK
            ) else (
                echo [ERROR] Missing output directory
                exit /b 1
            )
        ) else (
            echo [ERROR] Missing models directory
            exit /b 1
        )
    ) else (
        echo [ERROR] Missing data directory
        exit /b 1
    )
) else (
    echo [ERROR] Missing src directory
    exit /b 1
)
echo.

REM Check required files
echo [3/6] Checking required files...
set files=main.py config.yaml README.md LICENSE requirements.txt
for %%f in (%files%) do (
    if exist "%%f" (
        echo [OK] %%f exists
    ) else (
        echo [ERROR] %%f missing
        exit /b 1
    )
)
echo.

REM Check source modules
echo [4/6] Checking source modules...
set modules=utils.py tiling.py inference.py conversion.py spatial_nms.py dc_gnms.py
for %%m in (%modules%) do (
    if exist "src\%%m" (
        echo [OK] src\%%m exists
    ) else (
        echo [ERROR] src\%%m missing
        exit /b 1
    )
)
echo.

REM Check Python syntax
echo [5/6] Validating Python syntax...
python -m py_compile main.py
if errorlevel 1 (
    echo [ERROR] main.py has syntax errors
    exit /b 1
)
for %%f in (src\*.py) do (
    python -m py_compile "%%f"
    if errorlevel 1 (
        echo [ERROR] %%f has syntax errors
        exit /b 1
    )
)
echo [OK] All Python files have valid syntax
echo.

REM Check YAML files
echo [6/6] Validating YAML files...
python -c "import yaml; yaml.safe_load(open('config.yaml'))" 2>nul
if errorlevel 1 (
    echo [ERROR] config.yaml has errors
    exit /b 1
) else (
    echo [OK] config.yaml is valid
)
echo.

echo ==========================================
echo [SUCCESS] All validation checks passed!
echo ==========================================
echo.
echo Next steps:
echo 1. Install dependencies: conda env create -f environment.yml
echo 2. Download model weights (see models\README.md)
echo 3. Run test: python main.py --config config_test.yaml
echo.
pause
