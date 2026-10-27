"""
ITCD Domain-Aware - Conversion Module
Convert LabelMe JSON to GeoJSON with georeferencing
Extract from _spatial_nms.ipynb
Author: Agus Ambarwari
"""

import json
import rasterio
import os
import glob
import logging
from pathlib import Path
from typing import Dict, Any


logger = logging.getLogger(__name__)


def labelme_to_geojson(input_json_path: str, input_tif_path: str, output_geojson_path: str) -> None:
    """
    Convert LabelMe JSON to GeoJSON with georeferencing from TIF.
    
    Args:
        input_json_path: Path to LabelMe JSON file
        input_tif_path: Path to corresponding TIF file
        output_geojson_path: Path to output GeoJSON file
    """
    with open(input_json_path, 'r') as f:
        labelme_data = json.load(f)
    
    with rasterio.open(input_tif_path) as src:
        transform = src.transform
        crs = src.crs.to_string()
    
    geojson = {
        "type": "FeatureCollection",
        "name": Path(input_json_path).stem,
        "crs": {
            "type": "name",
            "properties": {
                "name": f"urn:ogc:def:crs:EPSG::{src.crs.to_epsg()}"
            }
        },
        "features": []
    }

    for shape in labelme_data['shapes']:
        if shape['shape_type'] == 'polygon':
            confidence_score = shape["score"]

            coords = []
            for point in shape['points']:
                geo_x, geo_y = transform * (point[0], point[1])
                coords.append([geo_x, geo_y])
            
            coords.append(coords[0])
            
            feature = {
                "type": "Feature",
                "properties": {
                    "Confidence_score": confidence_score
                },
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [coords]
                }
            }
            
            geojson['features'].append(feature)

    with open(output_geojson_path, 'w') as f:
        json.dump(geojson, f, indent=2)


def process_directory(input_json_dir: str, input_tif_dir: str, output_dir: str) -> None:
    """
    Process all JSON files in directory and convert to GeoJSON.
    
    Args:
        input_json_dir: Directory with LabelMe JSON files
        input_tif_dir: Directory with TIF files
        output_dir: Output directory for GeoJSON files
    """
    os.makedirs(output_dir, exist_ok=True)
    
    json_files = glob.glob(os.path.join(input_json_dir, "*.json"))
    
    if not json_files:
        logger.warning(f"No .json files found in {input_json_dir}")
        return

    logger.info(f"Found {len(json_files)} JSON files to process")
    
    success_count = 0
    for json_file in json_files:
        base_name = Path(json_file).stem
        
        tif_file = os.path.join(input_tif_dir, base_name + '.tif')
        
        if not os.path.exists(tif_file):
            logger.warning(f"No matching TIF file at {tif_file} for {Path(json_file).name}")
            continue
        
        output_file = os.path.join(output_dir, base_name + '.geojson')
        
        try:
            labelme_to_geojson(json_file, tif_file, output_file)
            success_count += 1
            if success_count % 20 == 0:
                logger.info(f"Processed {success_count}/{len(json_files)} files")
        except Exception as e:
            logger.error(f"Error processing {Path(json_file).name}: {str(e)}")
    
    logger.info(f"Successfully converted {success_count} files to GeoJSON")


def run_conversion(config: Dict[str, Any]) -> None:
    """
    Run conversion from LabelMe JSON to GeoJSON.
    
    Args:
        config: Configuration dictionary
    """
    input_json_dir = config['tiling']['output_dir']
    input_tif_dir = config['tiling']['output_dir']
    output_dir = config['postprocessing']['output_geojson_dir']
    
    logger.info(f"Converting LabelMe JSON to GeoJSON")
    logger.info(f"Input: {input_json_dir}")
    logger.info(f"Output: {output_dir}")
    
    process_directory(input_json_dir, input_tif_dir, output_dir)
    
    logger.info("Conversion completed successfully")
