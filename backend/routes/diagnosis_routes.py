import os
import shutil
import uuid
import base64
from fastapi import APIRouter, Depends, UploadFile, File, Form
from database import get_database
from models import ReportDB, Vitals, Prediction
from auth import get_current_user

from ml.image_predict import load_image_model, predict_image
from ml.text_predict import load_text_model, predict_text
from ml.vitals import analyze_vitals
from ml.symptoms_predict import predict_symptom_severity
from ml.fusion import fusion_decision
from ml.patient_report import generate_patient_report
from ml.doctor_report import generate_doctor_report

router = APIRouter()

image_model = load_image_model("models/ImageModelBothDatasets.pth")
text_model = load_text_model("models/text_model.joblib")

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def save_uploaded_file(upload_file: UploadFile) -> str:
    if not upload_file:
        return ""
    file_ext = os.path.splitext(upload_file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)

    upload_file.file.seek(0)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(upload_file.file, buffer)
    upload_file.file.seek(0)

    return f"http://localhost:8000/uploads/{unique_filename}"

def save_base64_image(base64_str: str) -> str:
    if not base64_str:
        return ""
    unique_filename = f"heatmap_{uuid.uuid4()}.jpg"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)
    
    with open(file_path, "wb") as fh:
        fh.write(base64.b64decode(base64_str))
        
    return f"http://localhost:8000/uploads/{unique_filename}"

@router.post("/patient/complete-diagnosis")
async def patient_complete_diagnosis(
    symptoms: str = Form(None),
    impression: str = Form(None),
    oxygen: float = Form(None),
    heart_rate: float = Form(None),
    temperature: float = Form(None),
    respiratory_rate: float = Form(None),
    image: UploadFile = File(None),
    current_user: dict = Depends(get_current_user)
):
    text_result = "Normal"
    vitals_result = "Normal"
    symptom_severity = "No Risk"

    if image:
        image_output = predict_image(image_model, image.file, generate_heatmap=True)
    else:
        image_output = {"fusion_probability": 0.1, "patient_result": "Normal"}
    image_result = image_output["patient_result"]

    if symptoms:
        sym_pred = predict_symptom_severity(symptoms)
        symptom_severity = sym_pred["severity"]

    if impression:
        text_pred = predict_text(text_model, impression)
        text_result = text_pred["label"]

    if oxygen is not None and heart_rate is not None and temperature is not None and respiratory_rate is not None:
        vitals_pred = analyze_vitals(oxygen, heart_rate, temperature, respiratory_rate)
        vitals_result = vitals_pred["vitals_result"]

    fusion_output = fusion_decision(image_output, text_result, vitals_result, symptom_severity)
    final_result = fusion_output["final_prediction"]

    image_url = save_uploaded_file(image)

    heatmap_b64 = image_output.get("heatmap_base64", None)
    heatmap_url = save_base64_image(heatmap_b64)

    patient_report = generate_patient_report(
        image_result=image_result, text_result=text_result, vitals_result=vitals_result,
        symptom_severity=symptom_severity, final_result=final_result
    )

    doctor_report = generate_doctor_report(
        image_result=image_result, text_result=text_result, vitals_result=vitals_result,
        symptom_severity=symptom_severity, final_result=final_result, heatmap_path=heatmap_url,
        image_probabilities=image_output.get("probabilities")
    )

    db = get_database()
    
    # Store compatibly with new database requirements
    # Save a generic copy into MongoDB Reports array backward compat check
    stored_report = {
        "patient_id": str(current_user["_id"]),
        "name": current_user["name"],
        "symptoms": symptoms,
        "impression": impression,
        "vitals": {
            "oxygen": oxygen,
            "heart_rate": heart_rate,
            "temperature": temperature,
            "respiratory_rate": respiratory_rate
        },
        "patient_report": patient_report,
        "doctor_report": doctor_report,
        "final_result": final_result,
        "image_url": image_url
    }
    await db["COMPAT_REPORTS"].insert_one(stored_report)
    
    # Save standard new database requirement mapping
    vitals_obj = Vitals(
        spo2=oxygen or 0.0,
        temperature=temperature or 0.0,
        heart_rate=heart_rate or 0.0,
        respiratory_rate=respiratory_rate or 0.0
    )
    prediction_obj = Prediction(disease=final_result, confidence=1.0, severity=symptom_severity)
    
    report_db = ReportDB(
        patient_id=str(current_user["_id"]),
        patient_name=current_user.get("name", "Unknown Patient"),
        symptoms=symptoms or "",
        clinical_notes=impression or "",
        vitals=vitals_obj,
        image_path=image_url,
        prediction=prediction_obj,
        patient_report=patient_report,
        doctor_report=doctor_report,
        status="pending"
    )
    result = await db["REPORTS"].insert_one(report_db.model_dump(by_alias=True, exclude={"id"}))
    patient_report["id"] = str(result.inserted_id)

    return patient_report


@router.post("/doctor/complete-diagnosis")
async def doctor_complete_diagnosis(
    symptoms: str = Form(None),
    impression: str = Form(None),
    oxygen: float = Form(None),
    heart_rate: float = Form(None),
    temperature: float = Form(None),
    respiratory_rate: float = Form(None),
    image: UploadFile = File(None),
    current_user: dict = Depends(get_current_user)
):
    text_result = "Normal"
    vitals_result = "Normal"
    symptom_severity = "No Risk"

    if image:
        image.file.seek(0)
        image_output = predict_image(image_model, image.file, generate_heatmap=True)
    else:
        image_output = {"fusion_probability": 0.1, "patient_result": "Normal", "probabilities": {}}
    image_result = image_output["patient_result"]

    if symptoms:
        sym_pred = predict_symptom_severity(symptoms)
        symptom_severity = sym_pred["severity"]

    if impression:
        text_pred = predict_text(text_model, impression)
        text_result = text_pred["label"]

    if oxygen is not None and heart_rate is not None and temperature is not None and respiratory_rate is not None:
        vitals_pred = analyze_vitals(oxygen, heart_rate, temperature, respiratory_rate)
        vitals_result = vitals_pred["vitals_result"]

    fusion_output = fusion_decision(image_output, text_result, vitals_result, symptom_severity)
    final_result = fusion_output["final_prediction"]

    image_url = save_uploaded_file(image)

    heatmap_b64 = image_output.get("heatmap_base64", None)
    heatmap_url = save_base64_image(heatmap_b64)

    doctor_report = generate_doctor_report(
        image_result=image_result, text_result=text_result, vitals_result=vitals_result,
        symptom_severity=symptom_severity, final_result=final_result, heatmap_path=heatmap_url,
        image_probabilities=image_output.get("probabilities")
    )

    patient_report = generate_patient_report(
        image_result=image_result, text_result=text_result, vitals_result=vitals_result,
        symptom_severity=symptom_severity, final_result=final_result
    )

    db = get_database()
    
    stored_report = {
        "doctor_uploader_id": str(current_user["_id"]),
        "name": current_user["name"],
        "symptoms": symptoms,
        "impression": impression,
        "vitals": {
            "oxygen": oxygen,
            "heart_rate": heart_rate,
            "temperature": temperature,
            "respiratory_rate": respiratory_rate
        },
        "patient_report": patient_report,
        "doctor_report": doctor_report,
        "final_result": final_result,
        "image_url": image_url
    }
    await db["COMPAT_REPORTS"].insert_one(stored_report)

    return doctor_report
