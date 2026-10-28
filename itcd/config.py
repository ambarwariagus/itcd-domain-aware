import os
from dataclasses import dataclass


@dataclass
class ITCDInferenceConfig:
    """
    Configuration parameters for the ITCD inference and geospatial post-processing pipeline.
    """
    # Detectron2 Model Paths
    trained_model_dir: str
    config_file: str = ""
    model_weights: str = ""

    # Detection & Threshold Parameters
    score_thresh_test: float = 0.5
    nms_thresh_test: float = 0.3

    # Tiling (Split Raster) Parameters
    tile_size: int = 1024
    overlap: int = 256

    # Georeferencing & Spatial NMS Parameters
    edge_shift_meters: float = 1.0
    spatial_iou_threshold: float = 0.5
    spatial_conf_threshold: float = 0.5
    area_threshold_m2: float = 2.0
    polygon_tolerance: float = 0.0

    def __post_init__(self):
        if not self.config_file:
            self.config_file = os.path.join(self.trained_model_dir, "config.yaml")
        if not self.model_weights:
            self.model_weights = os.path.join(self.trained_model_dir, "model_best_AP50.pth")
