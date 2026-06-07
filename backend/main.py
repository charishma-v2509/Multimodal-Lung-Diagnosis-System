# =========================================================
# IMPORTS
# =========================================================

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from database import connect_to_mongo, close_mongo_connection
from routes import auth_routes, doctor_routes, report_routes, diagnosis_routes

# =========================================================
# FASTAPI APP
# =========================================================

app = FastAPI(title="Multimodal Lung Diagnosis API - Upgraded")

# =========================================================
# CORS
# =========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================================================
# LIFECYCLE EVENTS
# =========================================================

@app.on_event("startup")
async def startup_db_client():
    await connect_to_mongo()

@app.on_event("shutdown")
async def shutdown_db_client():
    await close_mongo_connection()

# =========================================================
# STATIC FILES SETUP
# =========================================================

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# =========================================================
# ROUTERS
# =========================================================

app.include_router(auth_routes.router, tags=["Authentication"])
app.include_router(report_routes.router, tags=["Reports"])
app.include_router(doctor_routes.router, tags=["Doctor Actions"])
app.include_router(diagnosis_routes.router, tags=["Legacy Diagnosis"])

# =========================================================
# HEALTH CHECK
# =========================================================

@app.get("/")
def health_check():
    return {"status": "upgraded backend running successfully"}