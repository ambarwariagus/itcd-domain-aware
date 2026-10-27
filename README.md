# ITCD Domain-Aware Tree Crown Detection

Automated pipeline for Individual Tree Crown Detection (ITCD) from aerial imagery using Detectron2 and spatial NMS algorithms.

**Author:** Agus Ambarwari

## Features

- 🖼️ Automatic image tiling with overlap
- 🤖 Deep learning inference using Detectron2
- 🌍 Geospatial processing with coordinate transformation
- 🎯 Two NMS algorithms: Spatial NMS (Ball et al.) and DC-GNMS
- ⚙️ Configuration-driven workflow
- 📦 Single command execution

## Google Colab

Project ini dirancang untuk dijalankan melalui [Google Colab](notebooks/ITCD_Domain_Aware.ipynb). Notebook akan me-mount Google Drive, clone source code terbaru dari repository ini, menginstal `segment-geospatial` dan Detectron2, membuat konfigurasi, lalu menjalankan pipeline.

1. Buka `notebooks/ITCD_Domain_Aware.ipynb` di Google Colab dan aktifkan GPU.
2. Simpan input GeoTIFF dan model weights di Google Drive.
3. Ubah `DRIVE_ROOT`, `INPUT_IMAGE`, dan `MODEL_DIR` pada bagian konfigurasi notebook.
4. Jalankan cell secara berurutan.

### Model Weights

Download the pre-trained Detectron2 model from Google Drive:

**[📥 Download Model Weights (Google Drive)](https://drive.google.com/YOUR_LINK_HERE)**

Extract the downloaded file to the `models/` directory. The structure should be:

```
models/
└── 250525_R50_RESTOR_fold_0/
    ├── config.yaml
    └── model_best_AP50.pth
```

See [models/README.md](models/README.md) for detailed instructions.

## Quick Start

1. Open [`notebooks/ITCD_Domain_Aware.ipynb`](notebooks/ITCD_Domain_Aware.ipynb) in Google Colab.
2. Set the Colab runtime to **GPU**.
3. Run the Drive mount, GitHub clone, and dependency-installation cells.
4. Update the Google Drive paths in the configuration cell.
5. Run the pipeline cell.

The final GeoPackage is saved to `<OUTPUT_DIR>/final/tree_crowns.gpkg` in Google Drive.

## Running Individual Steps

The Colab notebook runs all stages by default. To resume a previous run, replace the pipeline command in its execution cell with one of the following:

```bash
python main.py --config /content/itcd-domain-aware/config_colab.yaml --step tiling
python main.py --config /content/itcd-domain-aware/config_colab.yaml --step inference
python main.py --config /content/itcd-domain-aware/config_colab.yaml --step conversion
python main.py --config /content/itcd-domain-aware/config_colab.yaml --step nms
```

## Configuration

The `config.yaml` file contains all pipeline parameters:

### Key Settings

**Input:**
- `image_path`: Path to input GeoTIFF

**Tiling:**
- `tile_size`: Tile dimensions (default: [1024, 1024])
- `overlap`: Overlap pixels (default: 256)

**Model:**
- `config_path`: Path to Detectron2 config
- `weights_path`: Path to model weights
- `score_threshold`: Detection confidence threshold (default: 0.5)
- `nms_threshold`: NMS threshold during inference (default: 0.3)

**Post-processing:**
- `nms_algorithm`: Choose between `spatial_nms` or `dc_gnms`

**Spatial NMS Parameters:**
- `iou_threshold`: IoU threshold for overlap removal (default: 0.5)
- `confidence_threshold`: Minimum confidence score (default: 0.5)
- `area_threshold`: Minimum area in m² (default: 2.0)
- `edge_shift`: Edge margin in meters (default: 1.0)

**DC-GNMS Parameters:**
- `box_filter_shift`: Center/edge zone margin (default: 1.0)
- `overlap_threshold`: IoA/IoMin threshold (default: 0.5)
- `cross_zone_threshold`: Cross-zone overlap tolerance (default: 0.15)

## NMS Algorithms

### Spatial NMS (Ball et al., 2023)

- Edge filtering with bounding box shift
- IoU-based overlap removal
- Confidence score filtering
- Recommended for: Simple overlapping scenarios

### DC-GNMS (Divide-and-Conquer Geometric NMS)

- Center/Edge zone division
- Intra-tile and Inter-tile NMS
- Cross-zone filtering
- Recommended for: Complex tiling scenarios with heavy overlap

Select the algorithm in `config.yaml`:

```yaml
postprocessing:
  nms_algorithm: "spatial_nms"  # or "dc_gnms"
```

## Output Structure

```
output/
├── tiles/              # Tiled images from step 1
│   ├── tile_0_0.tif
│   ├── tile_0_1.tif
│   └── predictions/    # Model predictions
├── geojson/            # GeoJSON with georeferencing
│   ├── tile_0_0.geojson
│   └── tile_0_1.geojson
├── final/              # Final merged results
│   └── tree_crowns.gpkg
└── pipeline.log        # Execution log
```

## Requirements

- Google account dan Google Drive
- Google Colab runtime dengan GPU aktif untuk inference
- GeoTIFF input dengan spatial reference system
- Model directory yang berisi `config.yaml` dan `model_best_AP50.pth`

Dependency Colab dipasang langsung dari `notebooks/ITCD_Domain_Aware.ipynb`: `segment-geospatial` dan Detectron2. Tidak diperlukan `requirements.txt`.

## Project Structure

```
itcd-domain-aware/
├── README.md
├── LICENSE
├── .gitignore
├── config.yaml
├── main.py
├── src/                         # Source pipeline yang dipakai Colab
│   ├── tiling.py
│   ├── inference.py
│   ├── conversion.py
│   ├── spatial_nms.py
│   ├── dc_gnms.py
│   └── utils.py
├── notebooks/
│   ├── ITCD_Domain_Aware.ipynb # Launcher Google Colab
│   └── README.md
├── models/
│   └── README.md
└── sample/                      # Contoh hasil
```

## Troubleshooting

### Model Not Found Error

Ensure you've downloaded the model weights and placed them in the correct directory:
```
models/250525_R50_RESTOR_fold_0/
```

### CUDA/GPU Issues

If you encounter GPU issues, edit the Detectron2 config to use CPU:
```yaml
MODEL:
  DEVICE: "cpu"
```

### Memory Issues

Reduce tile size in `config.yaml`:
```yaml
tiling:
  tile_size: [512, 512]
```

### No Output Polygons

Check the confidence threshold - it might be too high:
```yaml
postprocessing:
  spatial_nms:
    confidence_threshold: 0.3  # Lower value
```

## Example Workflow

In Google Colab:

1. Place a GeoTIFF at `MyDrive/ITCD_Domain_Aware/input/your_image.tif`.
2. Place model files at `MyDrive/ITCD_Domain_Aware/models/250525_R50_RESTOR_fold_0/`.
3. Open and run [`notebooks/ITCD_Domain_Aware.ipynb`](notebooks/ITCD_Domain_Aware.ipynb).
4. Retrieve the result from `MyDrive/ITCD_Domain_Aware/output/final/tree_crowns.gpkg`.

## Citation

If you use this code in your research, please cite:

```bibtex
@software{itcd_domain_aware,
  author = {Ambarwari, Agus},
  title = {ITCD Domain-Aware: Tree Crown Detection Pipeline},
  year = {2026},
  url = {https://github.com/ambarwariagus/itcd-domain-aware}
}
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Ball et al. (2023) for the Spatial NMS algorithm
- Detectron2 team for the detection framework
- segment-geospatial for the tiling utilities

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Contact

For questions or issues, please open an issue on GitHub or contact:
- **Author:** Agus Ambarwari
- **Email:** ambarwariagus@gmail.com

## Changelog

### Version 1.0.0 (2026-10-27)
- Initial release
- Support for Spatial NMS and DC-GNMS algorithms
- Configuration-driven pipeline
- Complete CLI interface
