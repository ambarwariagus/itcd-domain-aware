# 🚀 ITCD Domain-Aware - Google Colab Integration Guide

## 🎯 Goal
Enable users to run the full ITCD Domain-Aware pipeline directly in Google Colab using a single notebook, while keeping the main codebase in GitHub.

## 📋 Implementation Plan

### 1. Notebook Structure (Colab-ready)
- **Title**: `ITCD_Domain_Aware_Colab.ipynb`
- **Structure**:
  1. Mount Google Drive
  2. Clone GitHub repository
  3. Install dependencies (segment-geospatial, Detectron2)
  4. Configure paths to Google Drive
  5. Execute pipeline with configurable steps
  6. Download results

### 2. Colab Notebook Structure

```markdown
# ITCD Domain-Aware on Google Colab

## 📌 Setup (Run in order)

1. **Mount Google Drive**
   ```python
   from google.colab import drive
   drive.mount('/content/drive')
   ```

2. **Clone Repository**
   ```python
   !git clone https://github.com/ambarwariagus/itcd-domain-aware.git
   %cd itcd-domain-aware
   ```

3. **Install Dependencies**
   ```python
   !pip install segment-geospatial
   !git clone --depth 1 https://github.com/facebookresearch/detectron2.git /content/detectron2
   %cd /content/detectron2
   !pip install -e .
   %cd /content/itcd-domain-aware
   ```

4. **Configuration**
   - Set `config.yaml` paths to Google Drive locations:
   ```yaml
   input:
     image_path: "data/input/your_image.tif"  # Colab path
   ```

5. **Run Pipeline**
   ```bash
   python main.py --config config.yaml
   ```
   or specific steps:
   ```bash
   python main.py --config config.yaml --step tiling
   python main.py --config config.yaml --step inference
   python main.py --config config.yaml --step nms
   ```

### 2. File Structure in Colab
```
itcd-domain-aware/          # Cloned from GitHub
│
├── data/                          # User data (uploaded)
│   └── input/
│       └── your_image.tif
│
├── models/                          # Model weights (downloaded separately)
│   └── 250525_R50_RESTOR_fold_0/
│       ├── config.yaml
│       └── model_best_AP50.pth
│
├── output/                          # Output files
│   ├── tiles/
│   ├── predictions/
│   └── geojson/
│
├── notebooks/                       # Original notebooks (backup)
│   ├── _tiling.ipynb
│   ├── _prepare_label.ipynb
│   ├── _spatial_nms.ipynb
│   └── dc_gnms_algorithm.ipynb
│
└── sample/                          # Sample data & outputs (reference)
```

### 4. Sample Data Usage
- Use existing `sample/cmh01.tif` for testing
- Or upload your own GeoTIFF to Google Drive
- Update `config_test.yaml` with correct paths

### 5. Pipeline Execution
```bash
# Full pipeline
python main.py --config config_test.yaml

# Or specific steps:
python main.py --config config.yaml --step tiling
python main.py --config config.yaml --step inference
python main.py --config config.yaml --step conversion
python main.py --config config.yaml --step nms
```

### 5. Output Verification
- Check `output/tiles/` for tiled images
- Verify `output/geojson/` contains GeoJSON files
- Verify `output/final/tree_crowns.gpkg` exists
- View results in QGIS or Google Earth

---

## 📋 Implementation Details

### 📁 Source Code Structure
```
itcd-domain-aware/
├── main.py                          # CLI entry point
├── config.yaml                      # Default configuration
├── config_test.yaml                 # Test configuration with sample data
├── src/
│   ├── utils.py                     # Logging, validation, helpers
│   ├── tiling.py                    # Tile generation
│   ├── inference.py                # Detectron2 inference
│   ├── conversion.py                 # LabelMe → GeoJSON
│   ├── spatial_nms.py                # Ball et al. NMS algorithm
│   └── dc_gnms.py                    ✅ DC-GNMS support
│
├── notebooks/                         # Original notebooks (backup)
│   ├── ITCD_Domain_Aware.ipynb      # ✅ Colab launcher notebook
│   └── README.md                   # Notebook documentation
│
├── data/                            # Input data
│   └── input/                        ✅ User data location
│
├── models/                            ✅ Model weights
│   └── 250525_R50_RESTOR_fold_0/
│       ├── config.yaml
│       └── model_best_AP50.pth
│
├── output/                          ✅ Output directory
│   ├── tiles/
│   ├── geojson/
│   └── final/                        ✅ Final output
│
└── sample/                            ✅ Sample data & outputs
```

## 🧪 Testing with Sample Data

### Sample Data Setup
```bash
# Use existing sample data
python main.py --config config_test.yaml
```

### Expected Output
- `output/tiles/` - 169 tiled images
- `output/predictions/` - COCO JSON predictions
- `output/geojson/` - 167 georeferenced GeoJSON files
- `output/final/tree_crowns.gpkg` - Final merged GeoPackage

### 📊 Expected Output Volume
- **Tiles:** ~169 (1024×1024 with 256px overlap)
- **Predictions:** ~1,300-1,800 detections
- **Final GeoPackage:** ~1,300-1,500 tree crown polygons

---

## 🛠️ Implementation Details

### 1. Colab Notebook Structure

```python
# Cell 1: Mount Google Drive
from google.colab import drive
drive.mount('/content/drive')

# Cell 2: Clone repository
!git clone https://github.com/ambarwariagus/itcd-domain-aware.git
%cd /content/itcd-domain-aware

# Cell 3: Install dependencies
!pip install segment-geospatial
!git clone --depth 1 https://github.com/facebookresearch/detectron2.git /content/detectron2
%cd /content/detectron2
!pip install -e .

# Cell 4: Configure paths
config = {
    'input': {
        'image_path': '/content/drive/MyDrive/RESEARCH/itcd/input/your_image.tif',
        'output_dir': '/content/drive/MyDrive/ITCD_Domain_Aware/output/tiles'
    },
    'tiling': {
        'tile_size': [1024, 1024],
        'overlap': 256
    },
    'model': {
        'config_path': '/content/drive/MyDrive/ITCD_Domain_Aware/models/250525_R50_RESTOR_fold_0/config.yaml',
        'weights_path': '/content/drive/MyDrive/ITCD_Domain_Aware/models/250525_R50_RESTOR_fold_0/model_best_AP50.pth',
        'score_threshold': 0.5,
        'nms_threshold': 0.3
    },
    'postprocessing': {
        'nms_algorithm': 'spatial_nms',
        'iou_threshold': 0.5,
        'confidence_threshold': 0.5,
        'area_threshold': 2.0,
        'edge_shift': 1.0
    },
    'output': {
        'final_output_dir': '/content/drive/MyDrive/ITCD_Domain_Aware/output/final',
        'output_filename': 'tree_crowns.gpkg'
    }
}
```

### 5. Execution Flow
```python
# After configuration
run_pipeline(config, steps=['tiling', 'inference', 'conversion', 'nms'])
```

### 6. Verification
- Check output directory structure
- Verify final GeoPackage file exists
- Review `pipeline.log` for execution details
- Open `tree_crowns.gpkg` in QGIS or GeoPandas