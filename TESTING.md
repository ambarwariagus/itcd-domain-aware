# Testing Guide

This document explains how to test the ITCD Domain-Aware pipeline.

## Prerequisites

Before testing, ensure you have:

1. **Conda installed** (recommended) or Python 3.11.10
2. **Model weights** downloaded and placed in `models/250525_R50_RESTOR_fold_0/`
3. **Sample data** or your own GeoTIFF file

## Installation for Testing

### Option 1: Using Conda (Recommended)

```bash
# Create environment
conda env create -f environment.yml

# Activate environment
conda activate itcd-domain-aware
```

### Option 2: Using pip

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Linux/Mac)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Test 1: Validate Configuration

```bash
python main.py --config config_test.yaml --validate-only
```

Expected output:
```
Loading configuration from: config_test.yaml
Validating configuration...
✓ Configuration is valid

Configuration validation completed successfully!
```

## Test 2: Run with Sample Data

The repository includes sample data in `sample/cmh01.tif`.

```bash
# Use the test configuration
python main.py --config config_test.yaml
```

This will run the complete pipeline:
1. Tiling
2. Inference
3. Conversion to GeoJSON
4. Spatial NMS

Expected output location: `output/final/tree_crowns.gpkg`

## Test 3: Run Specific Steps

### Test Tiling Only

```bash
python main.py --config config_test.yaml --step tiling
```

Check output: `output/tiles/` should contain tiled images.

### Test Inference Only (after tiling)

```bash
python main.py --config config_test.yaml --step inference
```

Check output: `output/tiles/predictions/` should contain JSON files.

### Test NMS Only (after previous steps)

```bash
python main.py --config config_test.yaml --step nms
```

Check output: `output/final/tree_crowns.gpkg`

## Test 4: Test Different NMS Algorithms

### Test Spatial NMS

```bash
# config_test.yaml already uses spatial_nms by default
python main.py --config config_test.yaml --step nms
```

### Test DC-GNMS

Edit `config_test.yaml`:
```yaml
postprocessing:
  nms_algorithm: "dc_gnms"
```

Then run:
```bash
python main.py --config config_test.yaml --step nms
```

## Verification

After running the pipeline, verify the outputs:

### 1. Check Tiles
```bash
ls output/tiles/*.tif
```

Should show multiple tile files like `tile_0_0.tif`, `tile_0_1.tif`, etc.

### 2. Check Predictions
```bash
ls output/tiles/predictions/*.json
```

Should show JSON files with predictions.

### 3. Check GeoJSON
```bash
ls output/geojson/*.geojson
```

Should show GeoJSON files with georeferenced predictions.

### 4. Check Final Output
```bash
ls output/final/tree_crowns.gpkg
```

The final merged GeoPackage file.

### 5. Check Logs
```bash
cat output/pipeline.log
```

Review execution log for any errors or warnings.

## Load Results in QGIS

1. Open QGIS
2. Layer → Add Layer → Add Vector Layer
3. Browse to `output/final/tree_crowns.gpkg`
4. Click Add

You should see the detected tree crowns as polygons.

## Troubleshooting Tests

### Import Errors

If you get `ModuleNotFoundError`:
```bash
# Ensure environment is activated
conda activate itcd-domain-aware

# Or reinstall dependencies
pip install -r requirements.txt
```

### CUDA/GPU Errors

If you get CUDA errors, the model will automatically fall back to CPU (slower).

To force CPU mode, you can modify the Detectron2 config.

### Memory Errors

If you run out of memory:
1. Reduce tile size in config
2. Process fewer tiles at once
3. Close other applications

### No Detections

If final output has no polygons:
1. Check confidence threshold (try lowering it)
2. Review intermediate outputs
3. Check model weights are loaded correctly

## Performance Benchmarks

Expected processing times (approximate, varies by hardware):

| Step | Time (CPU) | Time (GPU) |
|------|-----------|-----------|
| Tiling | ~10s | ~10s |
| Inference (169 tiles) | ~30-60 min | ~5-10 min |
| Conversion | ~10s | ~10s |
| NMS | ~30s | ~30s |

**Total:** ~30-60 min (CPU) or ~5-10 min (GPU)

## Clean Up

To clean all outputs and start fresh:

```bash
# Windows
Remove-Item -Recurse -Force output\*

# Linux/Mac
rm -rf output/*
```

The `.gitkeep` files will be preserved.

## Expected Results

For the sample data (`sample/cmh01.tif`), you should expect:
- ~169 tiles
- ~1300-1800 initial detections
- ~1300-1500 detections after NMS

The exact numbers depend on the confidence threshold and NMS parameters.
