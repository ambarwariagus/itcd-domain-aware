"""
Simple Structure and Configuration Test
Tests without heavy dependencies
"""

import os
import sys
import yaml

def test_structure():
    """Test project structure"""
    print("[1/5] Testing project structure...")
    
    required_dirs = ['src', 'data', 'models', 'output', 'notebooks']
    for dir_name in required_dirs:
        if os.path.exists(dir_name):
            print(f"  [OK] {dir_name}/ exists")
        else:
            print(f"  [FAIL] {dir_name}/ missing")
            return False
    
    return True

def test_files():
    """Test required files"""
    print("\n[2/5] Testing required files...")
    
    required_files = [
        'main.py', 
        'config.yaml', 
        'config_test.yaml',
        'README.md', 
        'LICENSE',
        'requirements.txt',
        'environment.yml'
    ]
    
    for file_name in required_files:
        if os.path.exists(file_name):
            print(f"  [OK] {file_name} exists")
        else:
            print(f"  [FAIL] {file_name} missing")
            return False
    
    return True

def test_modules():
    """Test source modules"""
    print("\n[3/5] Testing source modules...")
    
    modules = [
        'src/__init__.py',
        'src/utils.py',
        'src/tiling.py',
        'src/inference.py',
        'src/conversion.py',
        'src/spatial_nms.py',
        'src/dc_gnms.py'
    ]
    
    for module in modules:
        if os.path.exists(module):
            print(f"  [OK] {module} exists")
        else:
            print(f"  [FAIL] {module} missing")
            return False
    
    return True

def test_configs():
    """Test YAML configurations"""
    print("\n[4/5] Testing YAML configurations...")
    
    configs = ['config.yaml', 'config_test.yaml']
    
    for config_file in configs:
        try:
            with open(config_file, 'r') as f:
                config = yaml.safe_load(f)
            
            # Check required sections
            required_sections = ['input', 'tiling', 'model', 'postprocessing', 'output', 'logging']
            for section in required_sections:
                if section in config:
                    print(f"  [OK] {config_file} - section '{section}' OK")
                else:
                    print(f"  [FAIL] {config_file} - missing section '{section}'")
                    return False
        except Exception as e:
            print(f"  [FAIL] {config_file} - Error: {e}")
            return False
    
    return True

def test_sample_data():
    """Test sample data"""
    print("\n[5/5] Testing sample data...")
    
    if os.path.exists('sample/cmh01.tif'):
        print(f"  [OK] sample/cmh01.tif exists")
    else:
        print(f"  [WARN] sample/cmh01.tif not found (optional)")
    
    if os.path.exists('models/250525_R50_RESTOR_fold_0/config.yaml'):
        print(f"  [OK] model config exists")
    else:
        print(f"  [WARN] model config not found")
    
    if os.path.exists('models/250525_R50_RESTOR_fold_0/model_best_AP50.pth'):
        print(f"  [OK] model weights exist")
    else:
        print(f"  [WARN] model weights not found")
    
    return True

def main():
    print("="*60)
    print("ITCD Domain-Aware - Structure & Configuration Test")
    print("="*60)
    print()
    
    results = []
    
    results.append(("Structure", test_structure()))
    results.append(("Files", test_files()))
    results.append(("Modules", test_modules()))
    results.append(("Configs", test_configs()))
    results.append(("Sample Data", test_sample_data()))
    
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
        print("\n[SUCCESS] All tests PASSED!")
        print("\nProject structure is correct and ready for deployment.")
        print("\nNext steps:")
        print("1. Install dependencies: conda env create -f environment.yml")
        print("2. Download model weights (see models/README.md)")
        print("3. Run pipeline: python main.py --config config_test.yaml")
        return 0
    else:
        print("\n[ERROR] Some tests FAILED!")
        print("Please check the errors above.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
