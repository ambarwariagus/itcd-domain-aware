# Model Weights

Model weights are not stored in this repository. Download them from Google Drive and place them in the Google Drive location configured in the Colab notebook:

```
MyDrive/ITCD_Domain_Aware/models/250525_R50_RESTOR_fold_0/
├── config.yaml
└── model_best_AP50.pth
```

**Google Drive download:** [placeholder](https://drive.google.com/YOUR_LINK_HERE)

To use a custom model, change `MODEL_DIR` in `notebooks/ITCD_Domain_Aware.ipynb`. The directory must contain a Detectron2 `config.yaml` and its matching `.pth` weights file.
