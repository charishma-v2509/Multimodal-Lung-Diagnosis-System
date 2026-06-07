from fastapi import APIRouter, HTTPException, status, Depends
from datetime import timedelta
from models import UserCreate, UserLogin, UserResponse, UserDB
from auth import get_password_hash, verify_password, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES, get_current_user
from database import get_database
from email_validator import validate_email, EmailNotValidError

router = APIRouter()

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate):
    db = get_database()
    
    # Check if user exists
    existing_user = await db["USERS"].find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
        
    try:
        # Validate email
        validate_email(user.email)
    except EmailNotValidError:
        raise HTTPException(status_code=400, detail="Invalid email format")

    # Hash password and insert
    hashed_password = get_password_hash(user.password)
    user_db = UserDB(**user.model_dump(exclude={"password"}), password=hashed_password)
    
    result = await db["USERS"].insert_one(user_db.model_dump(by_alias=True, exclude={"id"}))
    created_user = await db["USERS"].find_one({"_id": result.inserted_id})
    created_user["id"] = str(created_user["_id"])
    
    return created_user

from fastapi.security import OAuth2PasswordRequestForm

@router.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    db = get_database()
    print(f"Login attempt for: {form_data.username}")
    user = await db["USERS"].find_one({"email": form_data.username})
    
    if not user:
        print(f"User not found: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not verify_password(form_data.password, user["password"]):
        print(f"Password mismatch for: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    print(f"Login successful for: {form_data.username}")
        
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["email"], "role": user.get("role")}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer", "role": user.get("role")}

@router.post("/login")
async def login(user_login: UserLogin):
    db = get_database()
    user = await db["USERS"].find_one({"email": user_login.email})
    
    if not user or not verify_password(user_login.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["email"], "role": user.get("role")}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer", "role": user.get("role")}

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: dict = Depends(get_current_user)):
    return current_user

from typing import List
@router.get("/doctors", response_model=List[UserResponse])
async def get_all_doctors(current_user: dict = Depends(get_current_user)):
    db = get_database()
    cursor = db["USERS"].find({"role": "doctor"})
    doctors = await cursor.to_list(length=100)
    for doc in doctors:
        doc["id"] = str(doc["_id"])
    return doctors
