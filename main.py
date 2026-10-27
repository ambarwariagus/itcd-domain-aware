#!/usr/bin/env python
"""
ITCD Domain-Aware Tree Crown Detection Pipeline
Main CLI entry point
Author: Agus Ambarwari
"""

import argparse
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.utils import load_config, validate_config, setup_logging, create_directories
from src.tiling import run_tiling
from src.inference import run_inference
from src.conversion import run_conversion
from src.spatial_nms import run_spatial_nms
from src.dc_gnms import run_dc_gnms


def run_pipeline(config, steps=None):
    """
    Run the complete pipeline or specific steps.
    
    Args:
        config: Configuration dictionary
        steps: List of steps to run, or None for all steps
    """
    all_steps = ['tiling', 'inference', 'conversion', 'nms']
    
    if steps is None:
        steps = all_steps
    
    logger = setup_logging(config['logging'])
    
    logger.info("=" * 60)
    logger.info("ITCD Domain-Aware Tree Crown Detection Pipeline")
    logger.info("Author: Agus Ambarwari")
    logger.info("=" * 60)
    
    create_directories(config)
    
    # Step 1: Tiling
    if 'tiling' in steps:
        logger.info("\n[STEP 1/4] Tiling...")
        run_tiling(config)
    
    # Step 2: Inference
    if 'inference' in steps:
        logger.info("\n[STEP 2/4] Running inference...")
        run_inference(config)
    
    # Step 3: Conversion to GeoJSON
    if 'conversion' in steps:
        logger.info("\n[STEP 3/4] Converting to GeoJSON...")
        run_conversion(config)
    
    # Step 4: NMS
    if 'nms' in steps:
        logger.info("\n[STEP 4/4] Applying NMS...")
        nms_algorithm = config['postprocessing']['nms_algorithm']
        
        if nms_algorithm == 'spatial_nms':
            run_spatial_nms(config)
        elif nms_algorithm == 'dc_gnms':
            run_dc_gnms(config)
        else:
            raise ValueError(f"Unknown NMS algorithm: {nms_algorithm}")
    
    logger.info("\n" + "=" * 60)
    logger.info("Pipeline completed successfully!")
    logger.info(f"Output saved to: {os.path.join(config['output']['final_output_dir'], config['output']['output_filename'])}")
    logger.info("=" * 60)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='ITCD Domain-Aware Tree Crown Detection Pipeline',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run complete pipeline
  python main.py --config config.yaml
  
  # Run specific steps
  python main.py --config config.yaml --step tiling inference
  
  # Validate configuration only
  python main.py --config config.yaml --validate-only
        """
    )
    
    parser.add_argument(
        '--config',
        type=str,
        default='config.yaml',
        help='Path to configuration YAML file (default: config.yaml)'
    )
    
    parser.add_argument(
        '--step',
        nargs='+',
        choices=['tiling', 'inference', 'conversion', 'nms', 'all'],
        help='Specific steps to run (default: all steps)'
    )
    
    parser.add_argument(
        '--validate-only',
        action='store_true',
        help='Only validate configuration without running pipeline'
    )
    
    args = parser.parse_args()
    
    try:
        # Load configuration
        print(f"Loading configuration from: {args.config}")
        config = load_config(args.config)
        
        # Validate configuration
        print("Validating configuration...")
        validate_config(config)
        print("✓ Configuration is valid")
        
        if args.validate_only:
            print("\nConfiguration validation completed successfully!")
            return
        
        # Determine steps to run
        steps = None
        if args.step:
            if 'all' in args.step:
                steps = None
            else:
                steps = args.step
        
        # Run pipeline
        run_pipeline(config, steps)
        
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except ValueError as e:
        print(f"Configuration Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Pipeline failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
