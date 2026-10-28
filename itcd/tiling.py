import os
from samgeo.common import split_raster


def run_tiling(image_path: str, out_dir_tiles: str, tile_size: int = 1024, overlap: int = 256):
    """
    Split a large high-resolution orthophoto into fixed-size georeferenced tiles with overlap.

    Args:
        image_path: Path to the input GeoTIFF raster.
        out_dir_tiles: Directory where output image tiles will be saved.
        tile_size: Pixel dimension for tile width and height (default: 1024).
        overlap: Overlap in pixels between adjacent tiles (default: 256).
    """
    os.makedirs(out_dir_tiles, exist_ok=True)
    print(f"[*] Running raster split on: {image_path}")
    print(f"[*] Tile size: ({tile_size}, {tile_size}), Overlap: {overlap} px")
    split_raster(image_path, out_dir=out_dir_tiles, tile_size=(tile_size, tile_size), overlap=overlap)
    print(f"[v] Tiling completed in directory: {out_dir_tiles}")
