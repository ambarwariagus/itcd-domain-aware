"""
ITCD Domain-Aware - Tiling Module
Extract from _tiling.ipynb
Author: Agus Ambarwari
"""

import logging
from samgeo.common import split_raster
from typing import Dict, Any


logger = logging.getLogger(__name__)


def run_tiling(config: Dict[str, Any]) -> None:
    """
    Split large GeoTIFF image into smaller tiles with overlap.
    
    Args:
        config: Configuration dictionary
    """
    image_path = config['input']['image_path']
    output_dir = config['tiling']['output_dir']
    tile_size = tuple(config['tiling']['tile_size'])
    overlap = config['tiling']['overlap']
    
    logger.info(f"Tiling image: {image_path}")
    logger.info(f"Tile size: {tile_size}, Overlap: {overlap} pixels")
    logger.info(f"Output directory: {output_dir}")
    
    try:
        split_raster(
            image_path,
            out_dir=output_dir,
            tile_size=tile_size,
            overlap=overlap
        )
        logger.info("Tiling completed successfully")
    except Exception as e:
        logger.error(f"Tiling failed: {e}")
        raise
