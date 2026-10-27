"""
ITCD Domain-Aware Utility Functions
Author: Agus Ambarwari
"""

import logging
import os
import sys
from pathlib import Path
from typing import Dict, Any
import yaml


def setup_logging(logging_config: Dict[str, Any]) -> logging.Logger:
    """
    Setup logging configuration.
    
    Args:
        logging_config: Dictionary with logging settings
        
    Returns:
        Configured logger instance
    """
    level = getattr(logging, logging_config.get('level', 'INFO'))
    
    log_format = '%(asctime)s - %(levelname)s - %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    
    handlers = [logging.StreamHandler(sys.stdout)]
    
    if logging_config.get('save_log', False):
        log_file = logging_config.get('log_file', 'output/pipeline.log')
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        handlers.append(logging.FileHandler(log_file, mode='w'))
    
    logging.basicConfig(
        level=level,
        format=log_format,
        datefmt=date_format,
        handlers=handlers
    )
    
    return logging.getLogger(__name__)


def load_config(config_path: str) -> Dict[str, Any]:
    """
    Load configuration from YAML file.
    
    Args:
        config_path: Path to YAML configuration file
        
    Returns:
        Configuration dictionary
    """
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    return config


def validate_config(config: Dict[str, Any]) -> bool:
    """
    Validate configuration settings.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        True if valid, raises ValueError otherwise
    """
    required_keys = ['input', 'tiling', 'model', 'postprocessing', 'output', 'logging']
    
    for key in required_keys:
        if key not in config:
            raise ValueError(f"Missing required configuration section: {key}")
    
    if not os.path.exists(config['input']['image_path']):
        raise ValueError(f"Input image not found: {config['input']['image_path']}")
    
    model_config = config['model']['config_path']
    model_weights = config['model']['weights_path']
    
    if not os.path.exists(model_config):
        raise ValueError(f"Model config not found: {model_config}")
    
    if not os.path.exists(model_weights):
        raise ValueError(f"Model weights not found: {model_weights}")
    
    nms_algorithm = config['postprocessing']['nms_algorithm']
    if nms_algorithm not in ['spatial_nms', 'dc_gnms']:
        raise ValueError(f"Invalid NMS algorithm: {nms_algorithm}. Must be 'spatial_nms' or 'dc_gnms'")
    
    return True


def create_directories(config: Dict[str, Any]) -> None:
    """
    Create necessary output directories.
    
    Args:
        config: Configuration dictionary
    """
    dirs_to_create = [
        config['tiling']['output_dir'],
        config['postprocessing']['output_geojson_dir'],
        config['output']['final_output_dir'],
        os.path.join(config['tiling']['output_dir'], 'predictions')
    ]
    
    for directory in dirs_to_create:
        os.makedirs(directory, exist_ok=True)


def get_tiles_dir(config: Dict[str, Any]) -> str:
    """Get tiles directory path."""
    return config['tiling']['output_dir']


def get_predictions_dir(config: Dict[str, Any]) -> str:
    """Get predictions directory path."""
    return os.path.join(config['tiling']['output_dir'], 'predictions')


def get_geojson_dir(config: Dict[str, Any]) -> str:
    """Get GeoJSON directory path."""
    return config['postprocessing']['output_geojson_dir']


def get_final_output_path(config: Dict[str, Any]) -> str:
    """Get final output file path."""
    output_dir = config['output']['final_output_dir']
    output_filename = config['output']['output_filename']
    return os.path.join(output_dir, output_filename)
