import os
import shutil
import uuid
import json
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form, status
from typing import List

from database import get_database
from models import ReportDB, ReportResponse, Vitals, Prediction
from auth import get_current_patient, get_current_doctor, get_current_user
from pydantic import BaseModel
from bson import ObjectId

class AssignDoctorRequest(BaseModel):
    report_id: str
    doctor_id: str

# Note: In a fully integrated version, we would import the ML functions here
# from ml.image_predict import predict_image
# from ml.symptoms_predict import predict_symptom_severity
# ...

router = APIRouter()

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
    # Storing just the relative path/filename
    return file_path

@router.post("/upload", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
async def upload_report(
    symptoms: str = Form(""),
    clinical_notes: str = Form(""),
    spo2: float = Form(...),
    temperature: float = Form(...),
    heart_rate: float = Form(...),
    respiratory_rate: float = Form(None),
    image: UploadFile = File(...),
    current_user: dict = Depends(get_current_patient)
):
    db = get_database()
    
    # Save the file to the uploads directory
    saved_path = save_uploaded_file(image)
    if not saved_path:
        raise HTTPException(status_code=400, detail="Failed to save image")

    # In a full system, we would run the ML models here
    # Example placeholder result:
    prediction = Prediction(
        disease="Pending AI Inference",
        confidence=0.0,
        severity="Unknown"
    )

    vitals = Vitals(
        spo2=spo2,
        temperature=temperature,
        heart_rate=heart_rate,
        respiratory_rate=respiratory_rate
    )
    
    report_data = ReportDB(
        patient_id=str(current_user["_id"]),
        patient_name=current_user.get("name", "Unknown Patient"),
        symptoms=symptoms,
        clinical_notes=clinical_notes,
        vitals=vitals,
        image_path=saved_path,
        prediction=prediction,
        status="pending"
    )

    result = await db["REPORTS"].insert_one(report_data.model_dump(by_alias=True, exclude={"id"}))
    created_report = await db["REPORTS"].find_one({"_id": result.inserted_id})
    created_report["id"] = str(created_report["_id"])
    
    return created_report

@router.get("/reports", response_model=List[ReportResponse])
async def get_reports(current_user: dict = Depends(get_current_user)):
    db = get_database()
    
    query = {}
    if current_user["role"] == "doctor":
        query = {"assigned_doctor_id": str(current_user["_id"])}
    else:
        query = {"patient_id": str(current_user["_id"])}
        
    cursor = db["REPORTS"].find(query)
    reports = await cursor.to_list(length=100)
    for report in reports:
        report["id"] = str(report["_id"])
    return reports

@router.post("/assign-doctor")
async def assign_doctor(request: AssignDoctorRequest, current_user: dict = Depends(get_current_patient)):
    db = get_database()
    
    # Verify the report exists and belongs to the patient
    report = await db["REPORTS"].find_one({"_id": ObjectId(request.report_id), "patient_id": str(current_user["_id"])})
    if not report:
        raise HTTPException(status_code=404, detail="Report not found or unauthorized")
        
    # Verify the doctor exists
    doctor = await db["USERS"].find_one({"_id": ObjectId(request.doctor_id), "role": "doctor"})
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
        
    # Update the report
    await db["REPORTS"].update_one(
        {"_id": ObjectId(request.report_id)},
        {"$set": {"assigned_doctor_id": request.doctor_id}}
    )
    
    return {"message": "Report assigned successfully"}
