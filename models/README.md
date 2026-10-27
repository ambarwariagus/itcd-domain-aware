# Model Weights

This directory contains pre-trained Detectron2 model weights for tree crown detection.

## Download Instructions

The model weights are **not included** in this repository due to file size.

### Manual Download

1. Download the model from Google Drive:
   
   **[📥 Download Model Weights](https://drive.google.com/YOUR_LINK_HERE)**

2. Extract the downloaded file to this directory

3. Verify the structure:
   ```
   models/
   └── 250525_R50_RESTOR_fold_0/
       ├── config.yaml
       └── model_best_AP50.pth
   ```

### Automatic Download (Optional)

Run the download script:
```bash
python models/download_models.py
```

## Model Information

- **Architecture**: ResNet-50 + RESTOR
- **Training Fold**: 0
- **Metric**: Best AP50
- **Framework**: Detectron2
- **Size**: ~XXX MB

## Troubleshooting

If you encounter issues:
1. Ensure the directory structure matches exactly
2. Check file permissions
3. Verify the paths in `config.yaml`

## Custom Models

To use your own trained model:
1. Place the model files in `models/your_model_name/`
2. Update the paths in `config.yaml`:
   ```yaml
   model:
     config_path: "models/your_model_name/config.yaml"
     weights_path: "models/your_model_name/model_weights.pth"
   ```
