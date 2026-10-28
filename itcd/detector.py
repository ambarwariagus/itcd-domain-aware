import os
import glob
import json
import cv2
from tqdm import tqdm
from detectron2.config import get_cfg
from detectron2.engine import DefaultPredictor
from detectron2.evaluation.coco_evaluation import instances_to_coco_json


class ITCDDetector:
    """
    Detectron2 model inference wrapper for tree crown detection on orthophoto tiles.
    """
    def __init__(self, config_file: str, model_weights: str, score_thresh: float = 0.5, nms_thresh: float = 0.3):
        cfg = get_cfg()
        cfg.merge_from_file(config_file)
        cfg.MODEL.WEIGHTS = model_weights
        cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = score_thresh
        cfg.MODEL.ROI_HEADS.NMS_THRESH_TEST = nms_thresh

        self.predictor = DefaultPredictor(cfg)
        print(f"[v] Detectron2 model successfully loaded from: {model_weights}")

    def predict_directory(self, tiles_dir: str, output_pred_dir: str):
        """
        Run inference on all *.tif files in a directory and save predictions as COCO RLE JSON.

        Args:
            tiles_dir: Directory containing input .tif tiles.
            output_pred_dir: Directory to save prediction JSON files.
        """
        os.makedirs(output_pred_dir, exist_ok=True)
        tif_files = sorted(glob.glob(os.path.join(tiles_dir, "*.tif")))

        if not tif_files:
            print(f"[!] No .tif files found in {tiles_dir}")
            return

        print(f"[*] Starting Detectron2 inference on {len(tif_files)} tiles...")
        for img_path in tqdm(tif_files, desc="Tile inference"):
            base_name = os.path.basename(img_path)
            file_name, _ = os.path.splitext(base_name)

            im = cv2.imread(img_path)
            if im is None:
                continue

            outputs = self.predictor(im)
            instances_cpu = outputs["instances"].to("cpu")
            coco_predictions = instances_to_coco_json(instances_cpu, img_path)

            output_json_path = os.path.join(output_pred_dir, f"{file_name}.json")
            with open(output_json_path, "w") as f:
                json.dump(coco_predictions, f)

        print(f"[v] Inference complete. Results saved to: {output_pred_dir}")
