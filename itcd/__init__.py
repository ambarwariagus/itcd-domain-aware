"""
ITCD Domain-Aware Inference and Geospatial Post-Processing Package
"""

from itcd.config import ITCDInferenceConfig
from itcd.tiling import run_tiling
from itcd.detector import ITCDDetector
from itcd.converter import convert_rle_to_labelme
from itcd.georeference import labelme_to_geojson, batch_labelme_to_geojson
from itcd.spatial_nms import stitch_and_clean_pipeline
from itcd.pipeline import run_full_pipeline

__all__ = [
    "ITCDInferenceConfig",
    "run_tiling",
    "ITCDDetector",
    "convert_rle_to_labelme",
    "labelme_to_geojson",
    "batch_labelme_to_geojson",
    "stitch_and_clean_pipeline",
    "run_full_pipeline"
]
