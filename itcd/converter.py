import os
import glob
import json
import numpy as np
from skimage import measure
import pycocotools.mask as mask_util
from tqdm import tqdm
from typing import List, Dict


def close_contour(contour: np.ndarray) -> np.ndarray:
    """Ensure polygon contour is closed."""
    if not np.array_equal(contour[0], contour[-1]):
        contour = np.vstack((contour, contour[0]))
    return contour


def binary_mask_to_polygon(binary_mask: np.ndarray, tolerance: float = 0.0) -> List[List[float]]:
    """
    Convert a 2D binary mask to COCO-formatted flat polygon coordinates [x1, y1, x2, y2, ...].

    Args:
        binary_mask: 2D numpy array representing binary segmentation mask.
        tolerance: Polygon approximation tolerance.

    Returns:
        List of flat coordinate lists representing polygon vertices.
    """
    polygons = []
    if binary_mask.ndim != 2:
        raise ValueError("binary_mask_to_polygon requires a 2D mask input")

    padded_mask = np.pad(binary_mask, pad_width=1, mode='constant', constant_values=0)
    contours = measure.find_contours(padded_mask, 0.5)

    for contour in contours:
        contour = close_contour(contour)
        approx_polygon = measure.approximate_polygon(contour, tolerance)
        if len(approx_polygon) < 3:
            continue
        approx_polygon = np.flip(approx_polygon, axis=1)  # Swap from (row, col) to (x, y)
        segmentation = [0.0 if val < 0 else float(val) for val in approx_polygon.ravel()]
        polygons.append(segmentation)

    return polygons


def polygons_to_labelme_json(detections_data_list: List[Dict], image_name: str, height: int, width: int, label: str = "tree") -> Dict:
    """
    Assemble detected polygons and confidence scores into a LabelMe JSON structure.

    Args:
        detections_data_list: List of dictionaries containing polygon points and confidence score.
        image_name: Base filename of the target image tile.
        height: Height of the image tile in pixels.
        width: Width of the image tile in pixels.
        label: Label name for the detected objects (default: 'tree').

    Returns:
        Dictionary adhering to LabelMe JSON schema.
    """
    shapes = []
    for det_data in detections_data_list:
        poly_flat = det_data["polygon"]
        score = det_data["score"]

        points = []
        try:
            for i in range(0, len(poly_flat), 2):
                points.append([float(poly_flat[i]), float(poly_flat[i+1])])
        except IndexError:
            continue

        if len(points) < 3:
            continue

        shapes.append({
            "label": label,
            "score": score,
            "points": points,
            "group_id": None,
            "description": "",
            "shape_type": "polygon",
            "flags": {}
        })

    return {
        "version": "2.5.3",
        "flags": {},
        "shapes": shapes,
        "imagePath": image_name,
        "imageData": None,
        "imageHeight": height,
        "imageWidth": width
    }


def convert_rle_to_labelme(prediction_dir: str, output_labelme_dir: str, label: str = "tree", tolerance: float = 0.0):
    """
    Parse COCO RLE JSON detection outputs and convert them to LabelMe JSON containing pixel polygons.

    Args:
        prediction_dir: Directory containing COCO RLE prediction JSON files.
        output_labelme_dir: Destination directory for LabelMe JSON files.
        label: Class label for detected crowns (default: 'tree').
        tolerance: Contour approximation tolerance.
    """
    os.makedirs(output_labelme_dir, exist_ok=True)
    json_files = sorted(glob.glob(os.path.join(prediction_dir, "*.json"), recursive=False))

    print(f"[*] Starting RLE to LabelMe JSON conversion for {len(json_files)} files...")
    success_count = 0

    for json_file_path in tqdm(json_files, desc="Converting RLE -> Polygons"):
        file_basename = os.path.basename(json_file_path)
        try:
            with open(json_file_path, 'r') as f:
                rle_detections = json.load(f)

            if not isinstance(rle_detections, list) or not rle_detections:
                continue

            first_det = rle_detections[0]
            height, width = first_det["segmentation"]["size"]
            image_name = os.path.basename(first_det["image_id"])

            all_detections = []
            for det in rle_detections:
                score = det.get("score")
                rle = det.get("segmentation")
                if not rle:
                    continue

                binary_mask_2d = mask_util.decode(rle).astype(np.uint8)
                polygons = binary_mask_to_polygon(binary_mask_2d, tolerance=tolerance)

                for poly in polygons:
                    all_detections.append({
                        "polygon": poly,
                        "score": score
                    })

            if not all_detections:
                continue

            labelme_data = polygons_to_labelme_json(all_detections, image_name, height, width, label=label)
            out_file = os.path.join(output_labelme_dir, file_basename)
            with open(out_file, 'w') as f:
                json.dump(labelme_data, f, indent=2)

            success_count += 1
        except Exception as e:
            print(f"  [!] Failed to process {file_basename}: {e}")

    print(f"[v] LabelMe conversion complete. {success_count} files saved to: {output_labelme_dir}")
