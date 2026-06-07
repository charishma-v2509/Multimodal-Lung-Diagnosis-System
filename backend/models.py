from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Any
from datetime import datetime
from bson import ObjectId

class PyObjectId(str):
    @classmethod
    def __get_pydantic_core_schema__(cls, _source_type: Any, _handler: Any):
        from pydantic_core import core_schema
        return core_schema.union_schema([
            # check if it's an instance of ObjectId
            core_schema.is_instance_schema(ObjectId),
            # check if it's a string that can be parsed into an ObjectId
            core_schema.no_info_plain_validator_function(cls.validate),
        ])

    @classmethod
    def validate(cls, value):
        if not ObjectId.is_valid(value):
            raise ValueError("Invalid ObjectId")
        return str(value)

# ==========================================
# USERS
# ==========================================

class UserBase(BaseModel):
    name: str
    email: EmailStr
    role: str = Field(..., pattern="^(patient|doctor)$")

class UserCreate(UserBase):
    password: str

class UserDB(UserBase):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}

class UserResponse(UserBase):
    id: str

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}

class UserLogin(BaseModel):
    email: EmailStr
    password: str

# ==========================================
# REPORTS
# ==========================================

class Vitals(BaseModel):
    spo2: float
    temperature: float
    heart_rate: float
    respiratory_rate: Optional[float] = None

class Prediction(BaseModel):
    disease: str
    confidence: float
    severity: str

class ReportDB(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    patient_id: str
    patient_name: str = "Unknown Patient"
    assigned_doctor_id: Optional[str] = None
    symptoms: str
    clinical_notes: str
    vitals: Vitals
    image_path: str
    prediction: Prediction
    patient_report: dict = {}
    doctor_report: dict = {}
    status: str = "pending" # pending or reviewed
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}

class ReportResponse(BaseModel):
    id: str
    patient_id: str
    patient_name: str
    assigned_doctor_id: Optional[str] = None
    symptoms: str
    clinical_notes: str
    vitals: Vitals
    image_path: str
    prediction: Prediction
    patient_report: dict = {}
    doctor_report: dict = {}
    status: str
    created_at: datetime

# ==========================================
# DOCTOR REVIEWS
# ==========================================

class ReviewCreate(BaseModel):
    report_id: str
    comments: str
    prescription: str

class ReviewDB(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    report_id: str
    doctor_id: str
    comments: str
    prescription: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}

class ReviewResponse(BaseModel):
    id: str
    report_id: str
    doctor_id: str
    comments: str
    prescription: str
    created_at: datetime
