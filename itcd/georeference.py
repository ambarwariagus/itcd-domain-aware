import os
import json
import glob
from pathlib import Path
import rasterio
from tqdm import tqdm


def labelme_to_geojson(input_json_path: str, input_tif_path: str, output_geojson_path: str):
    """
    Transform LabelMe JSON pixel coordinates into georeferenced GeoJSON geographic coordinates
    using the affine transform matrix of the corresponding GeoTIFF tile.

    Args:
        input_json_path: Path to the input LabelMe JSON file.
        input_tif_path: Path to the matching georeferenced GeoTIFF tile.
        output_geojson_path: Destination path for the output GeoJSON file.
    """
    with open(input_json_path, 'r') as f:
        labelme_data = json.load(f)

    with rasterio.open(input_tif_path) as src:
        transform = src.transform
        epsg_code = src.crs.to_epsg()

    geojson = {
        "type": "FeatureCollection",
        "name": Path(input_json_path).stem,
        "crs": {
            "type": "name",
            "properties": {
                "name": f"urn:ogc:def:crs:EPSG::{epsg_code}"
            }
        },
        "features": []
    }

    for shape in labelme_data.get('shapes', []):
        if shape.get('shape_type') == 'polygon':
            confidence_score = shape.get("score", 0.0)
            coords = []
            for point in shape.get('points', []):
                geo_x, geo_y = transform * (point[0], point[1])
                coords.append([geo_x, geo_y])

            if len(coords) < 3:
                continue

            # Close polygon
            if coords[0] != coords[-1]:
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


def batch_labelme_to_geojson(input_json_dir: str, input_tif_dir: str, output_geojson_dir: str):
    """
    Process all LabelMe JSON files in a directory and georeference them against corresponding GeoTIFF tiles.

    Args:
        input_json_dir: Directory containing LabelMe JSON files.
        input_tif_dir: Directory containing GeoTIFF tiles.
        output_geojson_dir: Destination directory for GeoJSON outputs.
    """
    os.makedirs(output_geojson_dir, exist_ok=True)
    json_files = sorted(glob.glob(os.path.join(input_json_dir, "*.json")))

    if not json_files:
        print(f"[!] No .json files found in {input_json_dir}")
        return

    print(f"[*] Georeferencing {len(json_files)} LabelMe files to GeoJSON format...")
    for json_file in tqdm(json_files, desc="Georeferencing"):
        base_name = Path(json_file).stem
        tif_file = os.path.join(input_tif_dir, base_name + '.tif')

        if not os.path.exists(tif_file):
            continue

        output_file = os.path.join(output_geojson_dir, base_name + '.geojson')
        try:
            labelme_to_geojson(json_file, tif_file, output_file)
        except Exception as e:
            print(f"  [!] Error processing {base_name}: {e}")

    print(f"[v] GeoJSON conversion completed in directory: {output_geojson_dir}")
