# 🩺 Multimodal Medical Diagnosis Assistant

An end-to-end multimodal ML web application that fuses **clinical images, patient vitals, symptom data, and text reports** into a unified deep learning pipeline to assist in medical diagnosis.

## Why multimodal?

Most medical AI tools work on a single data type — just images, or just vitals. Real clinical diagnosis combines multiple signals. This system tackles the harder problem: **late-stage multimodal fusion** using a Transformer that learns to weigh each input modality dynamically.

This is an active research direction in clinical AI, and this project implements it end-to-end.

---

## 🔍 What It Does

This system mimics how a real clinician reasons — by combining *multiple sources of evidence* simultaneously rather than relying on a single data type.

- 📋 **Symptom Analysis** — Severity scoring via a trained sklearn classifier
- 🖼️ **Medical Image Inference** — CNN-based image model trained on dual medical datasets (~347 MB, ResNet/VGG backbone)
- 📝 **Clinical Text Understanding** — Text report model using NLP-based feature extraction
- ⚡ **Fusion Prediction** — Transformer-based fusion model that integrates all modalities for a final clinical outcome prediction

**Why this matters:** Most medical AI tools work on a single modality (just images or just vitals). This project tackles the harder, more realistic problem of *multimodal fusion* — which is an active area of research in clinical AI.

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | React + Vite |
| **Backend** | FastAPI (Python) |
| **ML Models** | PyTorch (CNN + Transformer), Scikit-learn |
| **Model Serving** | Custom inference pipeline via FastAPI endpoints |
| **Evaluation** | Custom fusion evaluation script with accuracy metrics |

---

## 🏗️ Architecture

```
multimodal/
├── backend/                    # FastAPI Python backend
│   ├── ml/                     # Inference and prediction logic
│   └── models/                 # Trained model files (PTH, Joblib) — git-ignored
├── frontend/                   # React + Vite frontend
├── evaluate_fusion.py          # Fusion model evaluation script
└── README.md
```

**ML Model Overview:**

| Model File | Type | Size | Purpose |
|---|---|---|---|
| `ImageModelBothDatasets.pth` | PyTorch CNN | ~347 MB | Medical image classification |
| `final_transformer_model.pth` | PyTorch Transformer | ~28.5 MB | Multimodal fusion |
| `symptom_severity_model_sklearn161.joblib` | Scikit-learn | — | Symptom severity scoring |
| `text_model.joblib` | Scikit-learn | — | Clinical text analysis |

---

## ⚠️ Model Setup (Required Before Running)

The trained model files exceed GitHub's file size limit and are hosted on Google Drive.

**Step 1:** Download all model files from Google Drive:
👉 [Google Drive — Model Files](https://drive.google.com/drive/u/0/folders/1GI4wy4oP_a75VNr-hlvSHxZGiHVdOQqr)

**Step 2:** Place all downloaded files inside `backend/models/`:

```
backend/models/
├── ImageModelBothDatasets.pth
├── final_transformer_model.pth
├── symptom_severity_model_sklearn161.joblib
├── symptom_severity_model_metadata_sklearn161.joblib
└── text_model.joblib
```

> `*.pth` and `*.joblib` files are excluded via `.gitignore` to keep the repo lightweight.

---

## 🚀 Local Setup

### Backend

```bash
cd backend

python -m venv venv

# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
uvicorn main:app --reload
```

Backend runs at → `http://127.0.0.1:8000`

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at → `http://localhost:5173`

---

## 📊 Evaluation

Run the fusion model evaluation to reproduce accuracy results:

```bash
# Activate your virtual environment first
python evaluate_fusion.py
```

This script runs inference across all modalities and reports combined prediction accuracy on the test set.

---

## 💡 Key Technical Highlights

- **Dual-dataset image model** — trained on two separate medical imaging datasets for better generalization
- **Transformer-based fusion** — cross-modal attention to weigh evidence from each input type dynamically
- **Sklearn versioning** — models saved and loaded with explicit sklearn version pinning (`sklearn161`) to avoid deserialization issues
- **Separation of concerns** — ML inference logic is cleanly isolated in `backend/ml/` for easy model swapping or retraining

---

## 🎯 Use Case

Designed as a **clinical decision support tool** — not a replacement for a physician, but a second-opinion assistant that surfaces risk signals from heterogeneous patient data in one unified interface.

---

*Built as a final-year B.Tech project in AI & ML.*
