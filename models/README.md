# Pre-Trained Model Weights

Due to GitHub's file size limitations, the trained Detectron2 model weights (`model_best_AP50.pth`, ~351 MB) are hosted externally on Google Drive.

## 📥 Download Link

You can download the model weights and configuration directory from Google Drive:

🔗 **[Download Model Folder (Google Drive)](https://drive.google.com/drive/folders/1zdY9J_X9LA5xmOaeynx_SOKfoS9aQCF9?usp=sharing)**

---

## 📂 Directory Structure

After downloading, place the folder `250525_R50_RESTOR_fold_0` inside this `models/` directory:

```text
models/
├── README.md
└── 250525_R50_RESTOR_fold_0/
    ├── config.yaml              # Detectron2 model architecture & hyperparameters
    └── model_best_AP50.pth      # Fine-tuned ResNet-50 weights (AP50 best checkpoint)
```

---

## 🔬 Model Specifications

| Parameter | Value |
| :--- | :--- |
| **Framework** | Facebook AI Research Detectron2 |
| **Architecture** | Mask R-CNN |
| **Backbone** | ResNet-50 with Feature Pyramid Network (FPN) |
| **Domain Pre-Training** | RESTOR / OAM-TCD domain-specific pre-training |
| **Input Channels** | 3 (RGB) |
| **Target Class** | Individual Tree Crown (`tree`) |
| **Checkpoint** | `model_best_AP50.pth` |

---

## 💻 Usage

In Python, point `ITCDInferenceConfig` to this directory:

```python
from itcd import ITCDInferenceConfig

config = ITCDInferenceConfig(
    trained_model_dir="models/250525_R50_RESTOR_fold_0",
    score_thresh_test=0.5,
    nms_thresh_test=0.3
)
```

For Google Colab workflows, see [`notebooks/run_inference.ipynb`](../notebooks/run_inference.ipynb).
