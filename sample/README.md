# Sample Datasets

Due to GitHub's repository and file size limits, large high-resolution aerial GeoTIFF rasters (`danum.tif`, etc., ~100MB) are hosted externally on Google Drive.

## 📥 Download Link

You can download the sample orthophoto datasets from Google Drive:

🔗 **[Download Sample Datasets (Google Drive)](https://drive.google.com/drive/folders/19z289BGBoVkyrhUSGPWl5eASGSdl-P4R?usp=sharing)**

---

## 📂 Expected Directory Structure

After downloading, place the sample `.tif` files directly inside this `sample/` directory:

```text
sample/
├── README.md
└── danum.tif               # Tropical forest canopy GeoTIFF (~100 MB)
```

---

## 🔬 Dataset Information

- **Data Type:** High-resolution aerial / UAV orthomosaic imagery (GeoTIFF)
- **Coordinate Reference System:** Georeferenced projected CRS (UTM / WGS 84)
- **Bands / Channels:** 3-channel RGB (or 4-channel RGBA)
- **Bit Depth:** 8-bit (`uint8`, 0–255 per channel)
- **Application:** Benchmarking Individual Tree Crown Delineation (ITCD) and testing the end-to-end inference pipeline.

---

## 💻 Quick Usage

In Python, execute the pipeline against the downloaded sample image:

```python
from itcd import ITCDInferenceConfig, run_full_pipeline

# 1. Setup configuration
config = ITCDInferenceConfig(
    trained_model_dir="models/250525_R50_RESTOR_fold_0",
    score_thresh_test=0.5,
    nms_thresh_test=0.3,
    tile_size=1024,
    overlap=256
)

# 2. Run inference on sample raster
cleaned_gdf = run_full_pipeline(
    orthophoto_path="sample/cmh01.tif",
    work_dir="sample",
    config=config,
    output_gpkg="sample/tree_crowns.gpkg"
)

print(f"Detected {len(cleaned_gdf)} tree crowns.")
```

For execution on Google Colab with GPU acceleration, refer to [`notebooks/run_inference.ipynb`](../notebooks/run_inference.ipynb).
