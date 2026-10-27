# Data Directory

This directory contains input data for the ITCD Domain-Aware pipeline.

## Structure

```
data/
└── input/          # Place your GeoTIFF files here
```

## Usage

1. Place your GeoTIFF file(s) in the `input/` directory
2. Update the `config.yaml` file with the correct path:
   ```yaml
   input:
     image_path: "data/input/your_image.tif"
   ```

## Requirements

- Input must be a valid GeoTIFF file with spatial reference
- Recommended: RGB or multispectral imagery
- File format: `.tif` or `.tiff`

## Note

Large data files (>100MB) are excluded from Git by default.
See `.gitignore` for details.
