"""
ITCD Domain-Aware - Inference Module
Extract from _prepare_label.ipynb
Author: Agus Ambarwari
"""

import os
import json
import cv2
import glob
import logging
import warnings
import numpy as np
from typing import Dict, Any
from detectron2.config import get_cfg
from detectron2.engine import DefaultPredictor
from detectron2.evaluation.coco_evaluation import instances_to_coco_json
from skimage import measure
import pycocotools.mask as mask_util

warnings.simplefilter("ignore")
logger = logging.getLogger(__name__)


def close_contour(contour):
    """Close contour if not already closed."""
    if not np.array_equal(contour[0], contour[-1]):
        contour = np.vstack((contour, contour[0]))
    return contour


def binary_mask_to_polygon(binary_mask, tolerance=0):
    """
    Convert binary mask to polygon format.
    
    Args:
        binary_mask: 2D binary mask
        tolerance: Approximation tolerance
        
    Returns:
        List of polygons in COCO format
    """
    polygons = []
    if binary_mask.ndim != 2:
        raise ValueError("binary_mask_to_polygon expects a 2D mask")
        
    padded_binary_mask = np.pad(binary_mask, pad_width=1, mode='constant', constant_values=0)
    contours = measure.find_contours(padded_binary_mask, 0.5)

    for contour in contours:
        contour = close_contour(contour)
        approx_polygon = measure.approximate_polygon(contour, tolerance)
        if len(approx_polygon) < 3:
            continue
        approx_polygon = np.flip(approx_polygon, axis=1)
        segmentation = [item for sublist in approx_polygon for item in sublist]
        segmentation = [0 if i < 0 else i for i in segmentation]
        polygons.append(segmentation)

    return polygons


def polygons_to_labelme_json(detections_data_list, image_name, height, width, label="tree"):
    """
    Convert polygon detections to LabelMe JSON format.
    
    Args:
        detections_data_list: List of detection data with polygons and scores
        image_name: Name of the image
        height: Image height
        width: Image width
        label: Label for detections
        
    Returns:
        LabelMe JSON dictionary
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
            logger.warning(f"Skipping malformed polygon in {image_name}")
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

    labelme_json = {
        "version": "2.5.3",
        "flags": {},
        "shapes": shapes,
        "imagePath": image_name,
        "imageData": None,
        "imageHeight": height,
        "imageWidth": width
    }
    return labelme_json


def run_inference(config: Dict[str, Any]) -> None:
    """
    Run inference on tiled images using Detectron2 model.
    
    Args:
        config: Configuration dictionary
    """
    logger.info("Loading Detectron2 model...")
    
    trained_model_dir = os.path.dirname(config['model']['config_path'])
    config_file = config['model']['config_path']
    model_path = config['model']['weights_path']
    
    cfg = get_cfg()
    cfg.merge_from_file(config_file)
    cfg.MODEL.WEIGHTS = model_path
    cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = config['model']['score_threshold']
    cfg.MODEL.ROI_HEADS.NMS_THRESH_TEST = config['model']['nms_threshold']
    
    predictor = DefaultPredictor(cfg)
    logger.info("Model loaded successfully")
    
    imgs_dir = config['tiling']['output_dir']
    pred_dir = os.path.join(imgs_dir, 'predictions')
    os.makedirs(pred_dir, exist_ok=True)
    
    image_files = glob.glob(os.path.join(imgs_dir, '*.tif'))
    logger.info(f"Found {len(image_files)} tiles to process")
    
    logger.info("Running predictions...")
    for idx, img_path in enumerate(image_files, 1):
        base_name = os.path.basename(img_path)
        file_name, _ = os.path.splitext(base_name)
        
        im = cv2.imread(img_path)
        outputs = predictor(im)
        
        output_file = os.path.join(pred_dir, f"{file_name}.json")
        predict_img = instances_to_coco_json(outputs["instances"].to("cpu"), img_path)
        with open(output_file, "w") as f:
            json.dump(predict_img, f)
        
        if idx % 20 == 0:
            logger.info(f"Processed {idx}/{len(image_files)} tiles")
    
    logger.info("Prediction complete!")
    
    logger.info("Converting predictions to LabelMe format...")
    convert_predictions_to_labelme(pred_dir, imgs_dir)
    logger.info("Conversion to LabelMe format complete!")


def convert_predictions_to_labelme(prediction_dir: str, output_dir: str) -> None:
    """
    Convert COCO RLE predictions to LabelMe JSON format.
    
    Args:
        prediction_dir: Directory with prediction JSON files
        output_dir: Directory to save LabelMe JSON files
    """
    json_files = glob.glob(os.path.join(prediction_dir, "*.json"))
    
    logger.info(f"Converting {len(json_files)} prediction files to LabelMe format")
    
    count = 0
    for i, json_file_path in enumerate(json_files, 1):
        file_basename = os.path.basename(json_file_path)
        
        try:
            with open(json_file_path, 'r') as f:
                rle_detections = json.load(f)

            if not isinstance(rle_detections, list) or not rle_detections:
                logger.warning(f"File {file_basename} is empty or malformed. Skipping.")
                continue
                
        except Exception as e:
            logger.warning(f"Failed to read {file_basename}: {e}. Skipping.")
            continue

        all_detections_data = []
        
        try:
            first_det = rle_detections[0]
            height, width = first_det["segmentation"]["size"]
            image_name = os.path.basename(first_det["image_id"])
        except Exception as e:
            logger.warning(f"Unexpected format in {file_basename}. Skipping. ({e})")
            continue

        for det_idx, det in enumerate(rle_detections):
            score = det.get("score")
            rle = det["segmentation"]
            try:
                binary_mask_2d = mask_util.decode(rle).astype(np.uint8)
            except Exception as e:
                logger.warning(f"Failed to decode RLE #{det_idx+1} in {file_basename}")
                continue
            
            polygons = binary_mask_to_polygon(binary_mask_2d)

            for poly_data in polygons:
                all_detections_data.append({
                    "polygon": poly_data,
                    "score": score
                })

        if not all_detections_data:
            continue

        labelme_data = polygons_to_labelme_json(
            all_detections_data,
            image_name, 
            height,
            width,
            label="tree"
        )
        
        output_filename = os.path.join(output_dir, file_basename)
        
        try:
            with open(output_filename, 'w') as f:
                json.dump(labelme_data, f, indent=2)
            count += 1
        except IOError as e:
            logger.error(f"Failed to save file {output_filename}: {e}")
        
        if i % 20 == 0:
            logger.info(f"Converted {i}/{len(json_files)} files")
    
    logger.info(f"Successfully converted {count} files to LabelMe JSON format")
