# Multimodal Medical Diagnosis Assistant

This is a multimodal machine learning web application designed for medical diagnosis assistance. It combines patient symptoms, vitals, text reports, and clinical images using a fusion model to evaluate and predict clinical outcomes.

## Project Structure

```
multimodal/
├── backend/            # FastAPI Python backend
│   ├── ml/             # Inference and prediction logic
│   └── models/         # Trained model files (PTH, Joblib) - [IGNORED BY GIT]
├── frontend/           # React + Vite frontend
├── evaluate_fusion.py  # Script to evaluate fusion models
└── README.md           # Project documentation (this file)
```

---

## ⚠️ Important: Downloading the Trained Models

Because the trained machine learning models are too large to be stored directly on GitHub (specifically the image model, which is ~347 MB), they are hosted on Google Drive.

Before running the application, you **must** download the model files and place them in the `backend/models/` directory:

1. **Download the models** from this Google Drive link:
   - [👉 Google Drive Link to Models (Replace with your link)](https://drive.google.com/drive/u/0/folders/1GI4wy4oP_a75VNr-hlvSHxZGiHVdOQqr)

2. **Place the downloaded files** in the `backend/models/` folder. The folder must contain:
   - `ImageModelBothDatasets.pth` (~347 MB)
   - `final_transformer_model.pth` (~28.5 MB)
   - `symptom_severity_model_sklearn161.joblib`
   - `symptom_severity_model_metadata_sklearn161.joblib`
   - `text_model.joblib`

These extensions (`*.pth` and `*.joblib`) are excluded from Git commits via `.gitignore` to prevent repository bloat and transfer failures.

---

## Installation & Setup

### 1. Backend Setup

Navigate to the backend directory, set up a virtual environment, install the dependencies, and start the server:

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start the backend server
uvicorn main:app --reload
```

The backend server will run on `http://127.0.0.1:8000`.

### 2. Frontend Setup

In a new terminal window, navigate to the frontend directory, install dependencies, and start the development server:

```bash
cd frontend

# Install packages
npm install

# Run development server
npm run dev
```

The frontend will run on `http://localhost:5173` (or the port shown in your terminal).

---

## Evaluation

You can run the evaluation script to test the fusion model's accuracy:

```bash
# Ensure your virtual environment is active
python evaluate_fusion.py
```
