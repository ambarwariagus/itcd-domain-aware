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

## Installation

### 1. Clone Repository

```bash
git clone https://github.com/ambarwariagus/itcd-domain-aware.git
cd itcd-domain-aware
```

### 2. Create Conda Environment

```bash
conda env create -f environment.yml
conda activate itcd-domain-aware
```

### 3. Download Model Weights

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

### 1. Prepare Your Data

Place your GeoTIFF file in `data/input/`:

```bash
cp your_image.tif data/input/
```

### 2. Update Configuration

Edit `config.yaml` to point to your input file:

```yaml
input:
  image_path: "data/input/your_image.tif"
```

### 3. Run Pipeline

```bash
python main.py --config config.yaml
```

Output will be saved to `output/final/tree_crowns.gpkg`

## Usage

### Run Complete Pipeline

```bash
python main.py --config config.yaml
```

### Run Specific Steps

```bash
# Only tiling
python main.py --config config.yaml --step tiling

# Tiling + Inference
python main.py --config config.yaml --step tiling inference

# Only NMS (if intermediate files exist)
python main.py --config config.yaml --step nms
```

### Validate Configuration

```bash
python main.py --config config.yaml --validate-only
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

- Python 3.11.10
- CUDA-capable GPU (recommended for inference)
- GeoTIFF input with spatial reference system
- ~8GB RAM minimum
- ~2GB disk space for model weights

## Project Structure

```
itcd-domain-aware/
├── README.md
├── LICENSE
├── .gitignore
├── environment.yml
├── requirements.txt
├── config.yaml
├── main.py
├── src/
│   ├── __init__.py
│   ├── tiling.py
│   ├── inference.py
│   ├── conversion.py
│   ├── spatial_nms.py
│   ├── dc_gnms.py
│   └── utils.py
├── data/
│   └── input/
├── models/
│   └── README.md
├── output/
├── notebooks/          # Original Jupyter notebooks
└── sample/             # Sample output (for reference)
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

For the sample data:

```bash
# 1. Activate environment
conda activate itcd-domain-aware

# 2. Update config to use sample data
# Edit config.yaml: input -> image_path: "sample/cmh01.tif"

# 3. Run pipeline
python main.py --config config.yaml

# 4. Check output
ls output/final/tree_crowns.gpkg
```

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
- **Email:** [Your email here]

## Changelog

### Version 1.0.0 (2026-10-27)
- Initial release
- Support for Spatial NMS and DC-GNMS algorithms
- Configuration-driven pipeline
- Complete CLI interface
