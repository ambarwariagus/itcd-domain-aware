import os
import sys
from itcd.config import ITCDInferenceConfig
from itcd.tiling import run_tiling
from itcd.detector import ITCDDetector
from itcd.converter import convert_rle_to_labelme
from itcd.georeference import batch_labelme_to_geojson
from itcd.spatial_nms import stitch_and_clean_pipeline


def run_full_pipeline(orthophoto_path: str, work_dir: str, config: ITCDInferenceConfig, output_gpkg: str = None):
    """
    Automated end-to-end execution of the ITCD inference pipeline:
    1. Orthophoto tiling (split raster with overlap)
    2. Detectron2 deep learning inference (COCO RLE)
    3. RLE mask decoding into LabelMe polygon JSON
    4. Coordinate transformation from pixel coordinates to GeoJSON (CRS matching input GeoTIFF)
    5. Tile edge shift, polygon stitching, Spatial NMS, and GeoPackage (.gpkg) export

    Args:
        orthophoto_path: Path to the input large GeoTIFF orthophoto.
        work_dir: Working directory for intermediate tiles, predictions, and geojson files.
        config: ITCDInferenceConfig instance with pipeline parameters.
        output_gpkg: Destination path for the clean GeoPackage output.

    Returns:
        GeoDataFrame of clean, deduplicated tree crown polygons.
    """
    sys.setrecursionlimit(5000)

    tiles_dir = os.path.join(work_dir, "tiles")
    predictions_dir = os.path.join(tiles_dir, "predictions")
    labelme_dir = os.path.join(tiles_dir, "labelme_output")
    geojson_dir = os.path.join(tiles_dir, "geojson")

    if output_gpkg is None:
        output_gpkg = os.path.join(work_dir, "tree_crowns.gpkg")

    # Step 1: Tiling
    print("=" * 60)
    print("STAGE 1: SPLIT RASTER (TILING)")
    print("=" * 60)
    run_tiling(orthophoto_path, tiles_dir, tile_size=config.tile_size, overlap=config.overlap)

    # Step 2: Inference
    print("=" * 60)
    print("STAGE 2: DETECTRON2 MODEL INFERENCE")
    print("=" * 60)
    detector = ITCDDetector(
        config_file=config.config_file,
        model_weights=config.model_weights,
        score_thresh=config.score_thresh_test,
        nms_thresh=config.nms_thresh_test
    )
    detector.predict_directory(tiles_dir, predictions_dir)

    # Step 3: Convert RLE to LabelMe JSON
    print("=" * 60)
    print("STAGE 3: CONVERT RLE MASKS TO LABELME JSON")
    print("=" * 60)
    convert_rle_to_labelme(predictions_dir, labelme_dir, label="tree", tolerance=config.polygon_tolerance)

    # Step 4: Georeferencing (GeoJSON)
    print("=" * 60)
    print("STAGE 4: GEOREFERENCING TO GEOJSON")
    print("=" * 60)
    batch_labelme_to_geojson(labelme_dir, tiles_dir, geojson_dir)

    # Step 5: Stitching & Spatial NMS to GPKG
    print("=" * 60)
    print("STAGE 5: STITCHING, SPATIAL NMS, & GPKG EXPORT")
    print("=" * 60)
    cleaned_gdf = stitch_and_clean_pipeline(
        geojson_dir=geojson_dir,
        tif_dir=tiles_dir,
        output_gpkg=output_gpkg,
        shift=config.edge_shift_meters,
        iou_threshold=config.spatial_iou_threshold,
        confidence_threshold=config.spatial_conf_threshold,
        area_threshold=config.area_threshold_m2
    )

    print("=" * 60)
    print(f"PIPELINE COMPLETED! Final output: {output_gpkg}")
    print("=" * 60)
    return cleaned_gdf
