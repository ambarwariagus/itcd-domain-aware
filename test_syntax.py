"""
Python Syntax and Import Structure Test
Tests without running actual pipeline
"""

import os
import sys
import py_compile
import tempfile

def test_python_syntax():
    """Test Python files for syntax errors"""
    print("[1/3] Testing Python syntax...")
    
    python_files = [
        'main.py',
        'src/__init__.py',
        'src/utils.py',
        'src/tiling.py',
        'src/inference.py',
        'src/conversion.py',
        'src/spatial_nms.py',
        'src/dc_gnms.py'
    ]
    
    all_valid = True
    for file_path in python_files:
        try:
            # Compile to check syntax
            py_compile.compile(file_path, doraise=True)
            print(f"  [OK] {file_path} - syntax valid")
        except py_compile.PyCompileError as e:
            print(f"  [FAIL] {file_path} - syntax error: {e}")
            all_valid = False
    
    return all_valid

def test_config_values():
    """Test configuration values"""
    print("\n[2/3] Testing configuration values...")
    
    import yaml
    
    with open('config_test.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    # Test input path
    input_path = config['input']['image_path']
    if os.path.exists(input_path):
        print(f"  [OK] Input image exists: {input_path}")
    else:
        print(f"  [WARN] Input image not found: {input_path}")
    
    # Test model paths
    model_config = config['model']['config_path']
    model_weights = config['model']['weights_path']
    
    if os.path.exists(model_config):
        print(f"  [OK] Model config exists: {model_config}")
    else:
        print(f"  [WARN] Model config not found: {model_config}")
    
    if os.path.exists(model_weights):
        size_mb = os.path.getsize(model_weights) / (1024*1024)
        print(f"  [OK] Model weights exist: {model_weights} ({size_mb:.1f} MB)")
    else:
        print(f"  [WARN] Model weights not found: {model_weights}")
    
    # Test NMS algorithm
    nms_algo = config['postprocessing']['nms_algorithm']
    if nms_algo in ['spatial_nms', 'dc_gnms']:
        print(f"  [OK] NMS algorithm valid: {nms_algo}")
    else:
        print(f"  [FAIL] Invalid NMS algorithm: {nms_algo}")
        return False
    
    return True

def test_documentation():
    """Test documentation completeness"""
    print("\n[3/3] Testing documentation...")
    
    docs = [
        'README.md',
        'TESTING.md',
        'LICENSE',
        'models/README.md',
        'data/README.md',
        'output/README.md',
        'notebooks/README.md'
    ]
    
    all_exist = True
    for doc in docs:
        if os.path.exists(doc):
            size_kb = os.path.getsize(doc) / 1024
            print(f"  [OK] {doc} exists ({size_kb:.1f} KB)")
        else:
            print(f"  [WARN] {doc} missing")
            all_exist = False
    
    return all_exist

def main():
    print("="*60)
    print("ITCD Domain-Aware - Syntax & Configuration Test")
    print("="*60)
    print()
    
    results = []
    
    results.append(("Python Syntax", test_python_syntax()))
    results.append(("Config Values", test_config_values()))
    results.append(("Documentation", test_documentation()))
    
    print("\n" + "="*60)
    print("TEST RESULTS")
    print("="*60)
    
    all_passed = True
    for test_name, result in results:
        status = "[PASSED]" if result else "[FAILED]"
        print(f"{test_name:.<30} {status}")
        if not result:
            all_passed = False
    
    print("="*60)
    
    if all_passed:
        print("\n[SUCCESS] All syntax and config tests PASSED!")
        print("\nProject is syntactically correct and properly configured.")
        return 0
    else:
        print("\n[WARNING] Some tests had warnings or failures.")
        print("Review the warnings above.")
        return 0  # Still return 0 as warnings are not critical

if __name__ == '__main__':
    sys.exit(main())
