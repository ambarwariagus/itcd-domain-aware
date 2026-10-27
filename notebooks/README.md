# Original Notebooks

This directory contains the original Jupyter notebooks that were used to develop the pipeline.

These notebooks are kept for reference and documentation purposes.

## Files

- **_tiling.ipynb** - Original tiling notebook using samgeo
- **_prepare_label.ipynb** - Detectron2 inference and RLE to LabelMe conversion
- **_spatial_nms.ipynb** - Spatial NMS algorithm (Ball et al.)
- **dc_gnms_algorithm.ipynb** - DC-GNMS algorithm implementation

## Usage

These notebooks are **not required** for running the pipeline. They are included as:
- Reference for the original workflow
- Documentation of algorithm development
- Examples for understanding the implementation

## Running Notebooks (Optional)

If you want to run the original notebooks:

```bash
# Install Jupyter
conda install jupyter

# Launch Jupyter
jupyter notebook
```

Then navigate to this directory and open the notebooks.

## Note

The production pipeline uses the Python modules in `src/` directory, which are extracted and refactored versions of these notebooks.
