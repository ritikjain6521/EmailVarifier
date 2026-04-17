from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import List
from datetime import timedelta
import asyncio
import json
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db import init_db, get_db, User
from app.services.email_validator import verify_email
from app.auth import (
    authenticate_user,
    create_access_token,
    get_current_user,
    register_user,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Run DB init
    await init_db()
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Production-ready Email Verification System with Auth",
    version=settings.VERSION,
    lifespan=lifespan
)

# ── CORS ─────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Schemas ───────────────────────────────────────────────────────────────────
class RegisterRequest(BaseModel):
    email: str
    password: str
    full_name: str

class VerifyRequest(BaseModel):
    email: str

class BulkVerifyRequest(BaseModel):
    emails: List[str]

# ── Public Routes ─────────────────────────────────────────────────────────────
@app.get("/")
def read_root():
    return {"status": "ok", "message": "Email Verifier API v2 is running with PostgreSQL"}

@app.post("/api/auth/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "email": user.email,
            "full_name": user.full_name,
            "plan": user.plan,
            "verifications_used": user.verifications_used,
            "verifications_limit": user.verifications_limit,
        },
    }

@app.post("/api/auth/register")
async def register(req: RegisterRequest, db: AsyncSession = Depends(get_db)):
    user = await register_user(db, req.email, req.password, req.full_name)
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "email": user.email,
            "full_name": user.full_name,
            "plan": user.plan,
            "verifications_used": user.verifications_used,
            "verifications_limit": user.verifications_limit,
        },
    }

# ── Protected Routes ──────────────────────────────────────────────────────────
@app.get("/api/me")
async def get_me(current_user: User = Depends(get_current_user)):
    return {
        "email": current_user.email,
        "full_name": current_user.full_name,
        "plan": current_user.plan,
        "verifications_used": current_user.verifications_used,
        "verifications_limit": current_user.verifications_limit,
    }

@app.post("/api/verify")
async def verify_single_email(req: VerifyRequest, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    try:
        result = await verify_email(req.email)
        # Update usage counter
        current_user.verifications_used += 1
        db.add(current_user)
        await db.commit()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/bulk-verify")
async def verify_multiple_emails(req: BulkVerifyRequest, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if len(req.emails) > 100:
        raise HTTPException(status_code=400, detail="Maximum 100 emails per request")

    tasks = [verify_email(email) for email in req.emails]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    final_results = []
    for r, email in zip(results, req.emails):
        if isinstance(r, Exception):
            final_results.append({"email": email, "error": str(r), "status": "error"})
        else:
            final_results.append(r)

    current_user.verifications_used += len(req.emails)
    db.add(current_user)
    await db.commit()
    
    return {"results": final_results, "total": len(final_results)}

@app.post("/api/upload-verify")
async def verify_uploaded_file(file: UploadFile = File(...), current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    content = await file.read()
    emails = []
    
    if file.filename.endswith(".json"):
        try:
            data = json.loads(content)
            if isinstance(data, list):
                emails = data
            elif isinstance(data, dict) and "emails" in data:
                emails = data["emails"]
            else:
                raise HTTPException(status_code=400, detail="Invalid JSON format. Expected an array of emails or '{ \"emails\": [...] }'")
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON file.")
    elif file.filename.endswith(".txt"):
        text = content.decode("utf-8")
        emails = [line.strip() for line in text.split("\n") if line.strip()]
    else:
        raise HTTPException(status_code=400, detail="Unsupported file format. Please upload .txt or .json")
        
    if not emails:
        raise HTTPException(status_code=400, detail="No emails found in the file.")
        
    if len(emails) > 500:
        raise HTTPException(status_code=400, detail="Maximum 500 emails per upload")
        
    tasks = [verify_email(email) for email in emails]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    final_results = []
    for r, email in zip(results, emails):
        if isinstance(r, Exception):
            final_results.append({"email": email, "error": str(r), "status": "error"})
        else:
            final_results.append(r)

    current_user.verifications_used += len(emails)
    db.add(current_user)
    await db.commit()

    return {"results": final_results, "total": len(final_results)}

@app.get("/api/stats")
async def get_stats(current_user: User = Depends(get_current_user)):
    return {
        "verifications_used": current_user.verifications_used,
        "verifications_limit": current_user.verifications_limit,
        "plan": current_user.plan,
        "usage_percent": round((current_user.verifications_used / max(current_user.verifications_limit, 1)) * 100, 1),
    }
