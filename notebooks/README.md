# Notebooks

## Google Colab Launcher

Use **[ITCD_Domain_Aware.ipynb](ITCD_Domain_Aware.ipynb)** as the supported interface for this project. It mounts Google Drive, clones the latest source from GitHub, installs `segment-geospatial` and Detectron2, generates a Colab-specific configuration, and runs `main.py` from the cloned repository.

Before running it, enable a GPU runtime in Google Colab and prepare Google Drive as follows:

```
MyDrive/ITCD_Domain_Aware/
├── input/
│   └── your_image.tif
├── models/
│   └── 250525_R50_RESTOR_fold_0/
│       ├── config.yaml
│       └── model_best_AP50.pth
└── output/
```

Update the paths in the notebook configuration cell if you use a different Google Drive directory.

## Original Development Notebooks

The following notebooks are retained only as development references:

- `_tiling.ipynb` — tiling with samgeo
- `_prepare_label.ipynb` — Detectron2 inference and RLE-to-LabelMe conversion
- `_spatial_nms.ipynb` — Spatial NMS implementation
- `dc_gnms_algorithm.ipynb` — DC-GNMS implementation

The production source code is maintained in `src/`; do not edit pipeline logic directly in the Colab launcher.
