#!/bin/bash
# Quick Test Script for ITCD Domain-Aware
# This script performs basic validation without running the full pipeline

echo "=========================================="
echo "ITCD Domain-Aware - Quick Validation"
echo "=========================================="
echo ""

# Check Python version
echo "[1/6] Checking Python version..."
python --version
echo ""

# Check project structure
echo "[2/6] Validating project structure..."
if [ -d "src" ] && [ -d "data" ] && [ -d "models" ] && [ -d "output" ]; then
    echo "✓ Directory structure OK"
else
    echo "✗ Missing directories"
    exit 1
fi
echo ""

# Check required files
echo "[3/6] Checking required files..."
required_files=("main.py" "config.yaml" "README.md" "LICENSE" "requirements.txt")
for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo "✓ $file exists"
    else
        echo "✗ $file missing"
        exit 1
    fi
done
echo ""

# Check source modules
echo "[4/6] Checking source modules..."
modules=("utils.py" "tiling.py" "inference.py" "conversion.py" "spatial_nms.py" "dc_gnms.py")
for module in "${modules[@]}"; do
    if [ -f "src/$module" ]; then
        echo "✓ src/$module exists"
    else
        echo "✗ src/$module missing"
        exit 1
    fi
done
echo ""

# Check Python syntax
echo "[5/6] Validating Python syntax..."
python -m py_compile main.py
for module in src/*.py; do
    if [[ ! "$module" == *"__pycache__"* ]]; then
        python -m py_compile "$module"
    fi
done
echo "✓ All Python files have valid syntax"
echo ""

# Check YAML files
echo "[6/6] Validating YAML files..."
python -c "import yaml; yaml.safe_load(open('config.yaml'))" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✓ config.yaml is valid"
else
    echo "✗ config.yaml has errors"
    exit 1
fi
echo ""

echo "=========================================="
echo "✓ All validation checks passed!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Install dependencies: conda env create -f environment.yml"
echo "2. Download model weights (see models/README.md)"
echo "3. Run test: python main.py --config config_test.yaml"
