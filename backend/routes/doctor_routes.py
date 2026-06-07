from fastapi import APIRouter, HTTPException, Depends, status
from bson import ObjectId

from database import get_database
from models import ReviewCreate, ReviewDB, ReviewResponse
from auth import get_current_doctor

router = APIRouter()

@router.post("/review", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
async def add_review(
    review_in: ReviewCreate,
    current_user: dict = Depends(get_current_doctor)
):
    db = get_database()
    
    # Check if the report exists
    try:
        report_obj_id = ObjectId(review_in.report_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid report_id format")

    report = await db["REPORTS"].find_one({"_id": report_obj_id})
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
        
    review_data = ReviewDB(
        report_id=review_in.report_id,
        doctor_id=str(current_user["_id"]),
        comments=review_in.comments,
        prescription=review_in.prescription
    )

    # Insert review
    result = await db["DOCTOR_REVIEWS"].insert_one(review_data.model_dump(by_alias=True, exclude={"id"}))
    
    # Update report status
    await db["REPORTS"].update_one(
        {"_id": report_obj_id},
        {"$set": {"status": "reviewed"}}
    )

    created_review = await db["DOCTOR_REVIEWS"].find_one({"_id": result.inserted_id})
    created_review["id"] = str(created_review["_id"])
    
    return created_review
