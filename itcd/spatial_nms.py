import os
import glob
import rasterio
import pandas as pd
import geopandas as gpd
from shapely.geometry import box
from typing import Optional


def calc_iou(shape1, shape2) -> float:
    """Calculate intersection-over-union (IoU) between two spatial geometries."""
    intersection_area = shape1.intersection(shape2).area
    union_area = shape1.union(shape2).area
    return intersection_area / union_area if union_area > 0 else 0.0


def filter_edge_crowns(gdf_tile: gpd.GeoDataFrame, tif_path: str, shift: float = 1.0) -> gpd.GeoDataFrame:
    """
    Shrink the bounding box of the tile by `shift` meters and drop crowns intersecting the tile margins.

    Args:
        gdf_tile: GeoDataFrame containing crowns for a single tile.
        tif_path: Path to the corresponding GeoTIFF tile.
        shift: Margin distance in meters to shrink from each edge (default: 1.0).

    Returns:
        Filtered GeoDataFrame with edge-intersecting crowns removed.
    """
    with rasterio.open(tif_path) as src:
        minx, miny, maxx, maxy = src.bounds.left, src.bounds.bottom, src.bounds.right, src.bounds.top

    shrunken_bbox = box(minx + shift, miny + shift, maxx - shift, maxy - shift)
    gdf_filtered = gdf_tile[gdf_tile.geometry.within(shrunken_bbox)]
    return gdf_filtered


def clean_crowns(
    crowns: gpd.GeoDataFrame,
    iou_threshold: float = 0.5,
    confidence_threshold: float = 0.5,
    area_threshold: float = 2.0,
    field: str = "Confidence_score"
) -> gpd.GeoDataFrame:
    """
    Filter overlapping crown polygons using Spatial Non-Maximum Suppression (NMS) with IoU and confidence thresholds.

    Args:
        crowns: Input GeoDataFrame with polygon geometries and confidence scores.
        iou_threshold: Minimum IoU overlap threshold to trigger suppression (default: 0.5).
        confidence_threshold: Minimum confidence score to retain (default: 0.5).
        area_threshold: Minimum polygon area in m² to retain (default: 2.0).
        field: Name of the confidence score column (default: 'Confidence_score').

    Returns:
        Cleaned GeoDataFrame of non-overlapping crown detections.
    """
    crowns = crowns[~crowns.is_empty & crowns.is_valid]
    crowns = crowns[crowns.area > area_threshold]
    crowns.reset_index(drop=True, inplace=True)

    cleaned_crowns = []
    print(f"[*] Running Spatial NMS on {len(crowns)} polygons...")

    for index, row in crowns.iterrows():
        if index % 1000 == 0 and index > 0:
            print(f"  Processing {index} / {len(crowns)} polygons...")

        intersecting_rows = crowns[crowns.intersects(row.geometry)]

        if len(intersecting_rows) > 1:
            iou_values = intersecting_rows.geometry.apply(lambda x: calc_iou(row.geometry, x))
            intersecting_rows = intersecting_rows.assign(iou=iou_values)

            # Select polygon with highest confidence score among overlapping candidates
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


def stitch_and_clean_pipeline(
    geojson_dir: str,
    tif_dir: str,
    output_gpkg: str,
    shift: float = 1.0,
    iou_threshold: float = 0.5,
    confidence_threshold: float = 0.5,
    area_threshold: float = 2.0,
    field: str = "Confidence_score"
) -> Optional[gpd.GeoDataFrame]:
    """
    Execute edge margin shifting, tile polygon stitching, spatial NMS deduplication, and export to GeoPackage (.gpkg).

    Args:
        geojson_dir: Directory containing per-tile GeoJSON polygon files.
        tif_dir: Directory containing GeoTIFF tiles.
        output_gpkg: Destination path for the final GeoPackage file.
        shift: Margin distance in meters for edge boundary filtering.
        iou_threshold: IoU overlap threshold for Spatial NMS.
        confidence_threshold: Minimum detection confidence score.
        area_threshold: Minimum crown area in m².
        field: Name of the confidence score column.

    Returns:
        GeoDataFrame of final cleaned polygons, or None if no valid crowns remain.
    """
    geojson_files = sorted(glob.glob(os.path.join(geojson_dir, "*.geojson")))
    if not geojson_files:
        print(f"[!] No GeoJSON files found in {geojson_dir}")
        return None

    print(f"[*] Phase 1: Stitching & Edge Bounding Box Shift ({shift}m) across {len(geojson_files)} files...")
    gdfs = []

    for geojson_file in geojson_files:
        gdf = gpd.read_file(geojson_file)
        if gdf.empty:
            continue

        base_name = os.path.splitext(os.path.basename(geojson_file))[0]
        tif_path = os.path.join(tif_dir, f"{base_name}.tif")

        if not os.path.exists(tif_path):
            gdfs.append(gdf)
            continue

        gdf_shifted = filter_edge_crowns(gdf, tif_path, shift=shift)
        gdfs.append(gdf_shifted)

    if not gdfs:
        print("[!] No valid polygons remaining after edge filtering.")
        return None

    merged_gdf = pd.concat(gdfs, ignore_index=True)
    merged_gdf = gpd.GeoDataFrame(merged_gdf, crs=gdfs[0].crs)
    print(f"[v] Total polygons after Stitching + Edge Shift: {len(merged_gdf)}")

    print(f"[*] Phase 2: Spatial NMS & Filtering (IoU={iou_threshold}, Score={confidence_threshold})...")
    cleaned_gdf = clean_crowns(
        crowns=merged_gdf,
        iou_threshold=iou_threshold,
        confidence_threshold=confidence_threshold,
        area_threshold=area_threshold,
        field=field
    )
    print(f"[v] Total clean polygons ready for export: {len(cleaned_gdf)}")

    os.makedirs(os.path.dirname(os.path.abspath(output_gpkg)), exist_ok=True)
    cleaned_gdf.to_file(output_gpkg, driver="GPKG")
    print(f"[v] GeoPackage file successfully saved to: {output_gpkg}")
    return cleaned_gdf
