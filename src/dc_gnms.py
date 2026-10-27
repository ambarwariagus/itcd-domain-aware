"""
ITCD Domain-Aware - DC-GNMS Module
Divide-and-Conquer Geometric NMS Algorithm
Extract from dc_gnms_algorithm.ipynb
Author: Agus Ambarwari
"""

import os
import glob
import logging
import pandas as pd
import geopandas as gpd
from shapely.geometry import box
from typing import Dict, Any


logger = logging.getLogger(__name__)


def get_crs_from_file(files):
    """Get CRS from first file in list."""
    if not files:
        return None
    try:
        gdf = gpd.read_file(files[0])
        return gdf.crs
    except Exception as e:
        logger.warning(f"Failed to read CRS: {e}")
        return None


def preprocess_tile(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Preprocess tile: remove invalid and small polygons."""
    gdf = gdf[~gdf.is_empty & gdf.is_valid]
    gdf = gdf[gdf.area > 2.0]
    return gdf.reset_index(drop=True)


def create_center_box(gdf: gpd.GeoDataFrame, shift: float = 1.0) -> gpd.GeoDataFrame:
    """Create center box by shrinking bounds."""
    bounds = gdf.total_bounds
    minx, miny, maxx, maxy = bounds
    
    center_box = box(minx + shift, miny + shift, maxx - shift, maxy - shift)
    
    return gpd.GeoDataFrame({'geometry': [center_box]}, crs=gdf.crs)


def apply_nms_by_score(gdf: gpd.GeoDataFrame, score_column: str, 
                       overlap_thresh: float, desc: str = "NMS") -> gpd.GeoDataFrame:
    """
    Apply NMS using IoA/IoMin metric.
    
    Args:
        gdf: GeoDataFrame with polygons
        score_column: Column name for scores
        overlap_thresh: Overlap threshold
        desc: Description for logging
        
    Returns:
        Filtered GeoDataFrame
    """
    if gdf.empty:
        return gdf
    
    gdf = gdf.sort_values(by=score_column, ascending=False).reset_index(drop=True)
    
    keep_indices = []
    suppressed_indices = set()
    
    for i in range(len(gdf)):
        if i in suppressed_indices:
            continue
            
        keep_indices.append(i)
        geom_A = gdf.loc[i].geometry
        area_A = geom_A.area
        
        for j in range(i + 1, len(gdf)):
            if j in suppressed_indices:
                continue
                
            geom_B = gdf.loc[j].geometry
            area_B = geom_B.area
            
            intersection_area = geom_A.intersection(geom_B).area
            if intersection_area == 0:
                continue
            
            min_area = min(area_A, area_B)
            overlap_ratio = intersection_area / min_area
            
            if overlap_ratio > overlap_thresh:
                suppressed_indices.add(j)

    return gdf.loc[keep_indices].copy()


def cross_zone_filter(gdf_edge: gpd.GeoDataFrame, gdf_center: gpd.GeoDataFrame, 
                      threshold: float) -> gpd.GeoDataFrame:
    """
    Remove edge polygons that overlap with center polygons above threshold.
    
    Args:
        gdf_edge: Edge zone GeoDataFrame
        gdf_center: Center zone GeoDataFrame
        threshold: Overlap threshold (IoA)
        
    Returns:
        Filtered edge GeoDataFrame
    """
    if gdf_edge.empty or gdf_center.empty:
        return gdf_edge

    logger.info(f"  [Cross-Zone] Comparing {len(gdf_edge)} EDGE vs {len(gdf_center)} CENTER (Tolerance: {threshold*100}%)...")
    
    joined = gpd.sjoin(gdf_edge, gdf_center, how="inner", predicate="intersects")
    
    if joined.empty:
        return gdf_edge

    indices_to_delete = set()
    
    for edge_idx, row in joined.iterrows():
        if edge_idx in indices_to_delete:
            continue
            
        center_idx = row['index_right']
        
        try:
            edge_geom = gdf_edge.geometry.loc[edge_idx]
            center_geom = gdf_center.geometry.loc[center_idx]
            
            intersection_area = edge_geom.intersection(center_geom).area
            
            if intersection_area == 0:
                continue
                
            ioa_edge = intersection_area / edge_geom.area
            
            if ioa_edge > threshold:
                indices_to_delete.add(edge_idx)
        except Exception:
            pass
            
    logger.info(f"  [Cross-Zone] Removing {len(indices_to_delete)} EDGE fragments overlapping > {threshold*100}% with CENTER...")
    
    gdf_edge_survivors = gdf_edge.drop(index=list(indices_to_delete)).reset_index(drop=True)
    return gdf_edge_survivors


def dc_gnms(geojson_dir: str, out_final: str, shift: float, 
            score_column: str, overlap_threshold: float, 
            cross_zone_threshold: float, simplify_tolerance: float) -> None:
    """
    Run DC-GNMS algorithm.
    
    Args:
        geojson_dir: Directory with GeoJSON files
        out_final: Output GPKG path
        shift: Box filter shift distance
        score_column: Column name for scores
        overlap_threshold: Overlap threshold for NMS
        cross_zone_threshold: Cross-zone overlap threshold
        simplify_tolerance: Geometry simplification tolerance
    """
    files = glob.glob(os.path.join(geojson_dir, "*.geojson"))
    if not files:
        logger.error(f"No .geojson files found in {geojson_dir}")
        return

    logger.info(f"Found {len(files)} GeoJSON files. Starting DIVIDE stage...\n")
    target_crs = get_crs_from_file(files)
    
    center_polygons_list = []
    edge_polygons_list = []

    for idx, file in enumerate(files, start=1):
        if idx % 100 == 0:
            logger.info(f"  ...processing file {idx} of {len(files)}: {os.path.basename(file)}")
            
        try:
            gdf = gpd.read_file(file)
            if gdf.empty:
                continue
            
            gdf = preprocess_tile(gdf)
            if gdf.empty:
                continue
            
            gdf_nms = apply_nms_by_score(gdf, score_column, overlap_threshold, desc="Intra-file NMS")
            
            center_box_gdf = create_center_box(gdf_nms, shift=shift)
            
            center_join = gpd.sjoin(gdf_nms, center_box_gdf, how="inner", predicate="within")
            center_indices = center_join.index
            gdf_center = gdf_nms.loc[center_indices]
            
            edge_indices = gdf_nms.index.difference(center_indices)
            gdf_edge = gdf_nms.loc[edge_indices]
            
            if not gdf_center.empty:
                center_polygons_list.append(gdf_center)
            if not gdf_edge.empty:
                edge_polygons_list.append(gdf_edge)
            
        except Exception as e:
            logger.warning(f"Failed to process file {os.path.basename(file)}: {e}")

    logger.info("\n--- STAGE 2: MERGE & INTER-NMS ---")
    
    gdf_center_final = gpd.GeoDataFrame(columns=['geometry'], crs=target_crs)
    if center_polygons_list:
        gdf_center_raw = pd.concat(center_polygons_list, ignore_index=True)
        logger.info(f"Total CENTER merged: {len(gdf_center_raw)}")
        gdf_center_final = apply_nms_by_score(gdf_center_raw, score_column, overlap_threshold, desc="Inter-file NMS (Center)")
        logger.info(f"CENTER final (clean): {len(gdf_center_final)}")

    gdf_edge_final = gpd.GeoDataFrame(columns=['geometry'], crs=target_crs)
    if edge_polygons_list:
        gdf_edge_raw = pd.concat(edge_polygons_list, ignore_index=True)
        logger.info(f"Total EDGE merged: {len(gdf_edge_raw)}")
        gdf_edge_final = apply_nms_by_score(gdf_edge_raw, score_column, overlap_threshold, desc="Inter-file NMS (Edge)")
        logger.info(f"EDGE final (clean): {len(gdf_edge_final)}")

    logger.info("\n--- STAGE 3: CONQUER (CROSS-ZONE & FINAL MERGE) ---")
    
    gdf_edge_survivors = cross_zone_filter(gdf_edge_final, gdf_center_final, cross_zone_threshold)
    logger.info(f"  EDGE polygons surviving as complete trees: {len(gdf_edge_survivors)}")
    
    logger.info("\nMerging CENTER and EDGE survivors into single dataset...")
    gdf_final = pd.concat([gdf_center_final, gdf_edge_survivors], ignore_index=True)
    
    if not gdf_final.empty:
        logger.info(f"  [Finishing] Simplifying geometry (tolerance {simplify_tolerance} meters)...")
        gdf_final["geometry"] = gdf_final.geometry.simplify(tolerance=simplify_tolerance, preserve_topology=True)
        gdf_final.set_crs(target_crs, inplace=True)
        gdf_final.to_file(out_final, driver="GPKG")
        logger.info(f"\n✅ SUCCESS! {len(gdf_final)} tree crown polygons saved to: {os.path.basename(out_final)}")
    else:
        logger.error("\n❌ Failed: No polygons remaining to save.")


def run_dc_gnms(config: Dict[str, Any]) -> None:
    """
    Run DC-GNMS algorithm.
    
    Args:
        config: Configuration dictionary
    """
    geojson_dir = config['postprocessing']['output_geojson_dir']
    output_gpkg = os.path.join(
        config['output']['final_output_dir'],
        config['output']['output_filename']
    )
    
    dcgnms_config = config['postprocessing']['dc_gnms']
    
    logger.info("Running DC-GNMS (Divide-and-Conquer Geometric NMS) algorithm")
    logger.info(f"Parameters:")
    logger.info(f"  - Box filter shift: {dcgnms_config['box_filter_shift']} m")
    logger.info(f"  - Overlap threshold: {dcgnms_config['overlap_threshold']}")
    logger.info(f"  - Cross-zone threshold: {dcgnms_config['cross_zone_threshold']}")
    logger.info(f"  - Simplify tolerance: {dcgnms_config['simplify_tolerance']} m")
    
    dc_gnms(
        geojson_dir=geojson_dir,
        out_final=output_gpkg,
        shift=dcgnms_config['box_filter_shift'],
        score_column="Confidence_score",
        overlap_threshold=dcgnms_config['overlap_threshold'],
        cross_zone_threshold=dcgnms_config['cross_zone_threshold'],
        simplify_tolerance=dcgnms_config['simplify_tolerance']
    )
    
    logger.info("DC-GNMS completed successfully")
