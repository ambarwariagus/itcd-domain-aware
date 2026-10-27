"""
ITCD Domain-Aware - Spatial NMS Module
Ball et al. (2023) Spatial NMS Algorithm
Extract from _spatial_nms.ipynb
Author: Agus Ambarwari
"""

import os
import glob
import logging
import rasterio
import pandas as pd
import geopandas as gpd
from shapely.geometry import box
from typing import Dict, Any


logger = logging.getLogger(__name__)


def calc_iou(shape1, shape2):
    """Calculate IoU (Intersection over Union) of two polygons."""
    intersection_area = shape1.intersection(shape2).area
    union_area = shape1.union(shape2).area
    return intersection_area / union_area if union_area > 0 else 0


def clean_crowns(crowns: gpd.GeoDataFrame,
                 iou_threshold: float = 0.5,
                 confidence_threshold: float = 0.5,
                 area_threshold: float = 2.0,
                 field: str = "Confidence_score") -> gpd.GeoDataFrame:
    """
    Clean overlapping polygons using NMS with IoU threshold.
    
    Args:
        crowns: GeoDataFrame with tree crown polygons
        iou_threshold: IoU threshold for overlap removal
        confidence_threshold: Minimum confidence score
        area_threshold: Minimum area (m²) to keep
        field: Field name for confidence scores
        
    Returns:
        Cleaned GeoDataFrame
    """
    crowns = crowns[~crowns.is_empty & crowns.is_valid]
    crowns = crowns[crowns.area > area_threshold]
    crowns.reset_index(drop=True, inplace=True)

    cleaned_crowns = []
    logger.info(f"Starting NMS cleaning on {len(crowns)} polygons...")

    for index, row in crowns.iterrows():
        if index % 1000 == 0 and index > 0:
            logger.info(f"  Processing {index} / {len(crowns)} polygons...")

        intersecting_rows = crowns[crowns.intersects(row.geometry)]

        if len(intersecting_rows) > 1:
            iou_values = intersecting_rows.geometry.apply(lambda x: calc_iou(row.geometry, x))
            intersecting_rows = intersecting_rows.assign(iou=iou_values)

            match = intersecting_rows[intersecting_rows["iou"] > iou_threshold].nlargest(1, field)

            if len(match) > 0 and match["iou"].iloc[0] < 1:
                continue
        else:
            match = row.to_frame().T

        cleaned_crowns.append(match)

    if cleaned_crowns:
        crowns_out = pd.concat(cleaned_crowns, ignore_index=True)
        if "iou" in crowns_out.columns:
            crowns_out = crowns_out.drop("iou", axis=1)
    else:
        crowns_out = gpd.GeoDataFrame()

    if not isinstance(crowns_out, gpd.GeoDataFrame):
        crowns_out = gpd.GeoDataFrame(crowns_out, crs=crowns.crs)
    else:
        crowns_out = crowns_out.set_crs(crowns.crs, allow_override=True)

    if confidence_threshold > 0 and field in crowns_out.columns:
        crowns_out[field] = pd.to_numeric(crowns_out[field])
        crowns_out = crowns_out[crowns_out[field] >= confidence_threshold]

    return crowns_out.reset_index(drop=True)


def filter_edge_crowns(gdf_tile, tif_path, shift=1.0):
    """
    Filter edge crowns using bounding box shift mechanism.
    Remove all trees that touch or cross the boundary.
    
    Args:
        gdf_tile: GeoDataFrame with tile polygons
        tif_path: Path to TIF file for boundary
        shift: Shift distance in meters
        
    Returns:
        Filtered GeoDataFrame
    """
    with rasterio.open(tif_path) as src:
        minx, miny, maxx, maxy = src.bounds.left, src.bounds.bottom, src.bounds.right, src.bounds.top
        
    shrunken_bbox = box(minx + shift, miny + shift, maxx - shift, maxy - shift)
    
    gdf_filtered = gdf_tile[gdf_tile.geometry.within(shrunken_bbox)]
    
    return gdf_filtered


def stitch_and_clean_pipeline(geojson_dir: str, tif_dir: str, output_gpkg: str, 
                               iou_threshold: float = 0.5,
                               confidence_threshold: float = 0.5,
                               area_threshold: float = 2.0,
                               shift: float = 1.0) -> None:
    """
    Complete pipeline: stitch tiles, filter edges, and apply NMS.
    
    Args:
        geojson_dir: Directory with GeoJSON files
        tif_dir: Directory with TIF files
        output_gpkg: Output GeoPackage path
        iou_threshold: IoU threshold for NMS
        confidence_threshold: Minimum confidence score
        area_threshold: Minimum area threshold
        shift: Edge shift distance in meters
    """
    geojson_files = glob.glob(os.path.join(geojson_dir, "*.geojson"))
    
    if not geojson_files:
        logger.error(f"No GeoJSON files found in {geojson_dir}")
        return

    logger.info(f"Stage 1: Stitching & Edge Bounding Box Shift ({shift}m) on {len(geojson_files)} files...")
    
    gdfs = []
    for geojson_file in geojson_files:
        gdf = gpd.read_file(geojson_file)
        if gdf.empty:
            continue
            
        base_name = os.path.splitext(os.path.basename(geojson_file))[0]
        tif_path = os.path.join(tif_dir, f"{base_name}.tif")
        
        if not os.path.exists(tif_path):
            logger.warning(f"TIF file {base_name}.tif not found. Shift skipped for this file.")
            gdfs.append(gdf)
            continue
            
        gdf_shifted = filter_edge_crowns(gdf, tif_path, shift=shift)
        gdfs.append(gdf_shifted)
        
    merged_gdf = pd.concat(gdfs, ignore_index=True)
    merged_gdf = gpd.GeoDataFrame(merged_gdf, crs=gdfs[0].crs)
    logger.info(f"Total polygons after Stitching + Edge Shift: {len(merged_gdf)}")
    
    logger.info("\nStage 2: Cleaning (NMS) & Filtering...")
    
    cleaned_gdf = clean_crowns(
        crowns=merged_gdf, 
        iou_threshold=iou_threshold,
        confidence_threshold=confidence_threshold,
        area_threshold=area_threshold,
        field="Confidence_score"
    )
    
    logger.info(f"Total final polygons (ready for export): {len(cleaned_gdf)}")
    
    cleaned_gdf.to_file(output_gpkg, driver="GPKG")
    logger.info(f"\nCompleted! Clean file saved to: {output_gpkg}")


def run_spatial_nms(config: Dict[str, Any]) -> None:
    """
    Run Spatial NMS algorithm (Ball et al.).
    
    Args:
        config: Configuration dictionary
    """
    geojson_dir = config['postprocessing']['output_geojson_dir']
    tif_dir = config['tiling']['output_dir']
    output_gpkg = os.path.join(
        config['output']['final_output_dir'],
        config['output']['output_filename']
    )
    
    nms_config = config['postprocessing']['spatial_nms']
    
    logger.info("Running Spatial NMS (Ball et al.) algorithm")
    logger.info(f"Parameters:")
    logger.info(f"  - IoU threshold: {nms_config['iou_threshold']}")
    logger.info(f"  - Confidence threshold: {nms_config['confidence_threshold']}")
    logger.info(f"  - Area threshold: {nms_config['area_threshold']} m²")
    logger.info(f"  - Edge shift: {nms_config['edge_shift']} m")
    
    stitch_and_clean_pipeline(
        geojson_dir=geojson_dir,
        tif_dir=tif_dir,
        output_gpkg=output_gpkg,
        iou_threshold=nms_config['iou_threshold'],
        confidence_threshold=nms_config['confidence_threshold'],
        area_threshold=nms_config['area_threshold'],
        shift=nms_config['edge_shift']
    )
    
    logger.info("Spatial NMS completed successfully")
