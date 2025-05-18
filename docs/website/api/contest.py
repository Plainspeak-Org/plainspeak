"""
Contest API Backend for PlainSpeak Plugin Development Contest.
"""

import os
import uuid
from datetime import datetime
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException
from github import Github, GithubException
from pydantic import BaseModel, EmailStr, HttpUrl
from sqlalchemy import Boolean, Column, DateTime, Float, String, Text, create_engine, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

# Database setup
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./contest.db")
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# Placeholder email functions - IMPLEMENT THESE
async def send_registration_confirmation(email: str, name: str, participant_id: str):
    """Placeholder for sending registration confirmation."""
    print(f"Registration confirmation for {name} ({email}, ID: {participant_id}) - implement actual sending")


async def send_submission_confirmation(email: str, name: str):
    """Placeholder for sending submission confirmation."""
    print(f"Submission confirmation for {name} ({email}) - implement actual sending")


# Models
class Participant(Base):
    __tablename__ = "participants"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    github_username = Column(String, unique=True, nullable=False)
    category = Column(String, nullable=False)
    idea_description = Column(Text, nullable=False)
    registered_at = Column(DateTime, default=datetime.utcnow)
    submission_url = Column(String)
    submission_date = Column(DateTime)
    judging_complete = Column(Boolean, default=False)
    final_score = Column(Float)


class Registration(BaseModel):
    name: str
    email: EmailStr
    github_username: str
    category: str
    idea_description: str


class Submission(BaseModel):
    participant_id: str
    repository_url: HttpUrl
    description: str
    video_url: Optional[HttpUrl]


# Create tables
Base.metadata.create_all(bind=engine)

# FastAPI app
app = FastAPI()


# Dependencies
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def verify_github_repo(url: str, github_token: str) -> bool:
    """Verify that the GitHub repository exists and contains required files."""
    try:
        g = Github(github_token)
        repo = g.get_repo(url.replace("https://github.com/", ""))

        required_files = ["plugin.yaml", "plugin.py", "README.md"]
        for file in required_files:
            try:
                repo.get_contents(file)
            except GithubException:
                return False
        return True
    except GithubException:
        return False


@app.post("/register")
async def register_participant(registration: Registration, db: Session = Depends(get_db)):
    """Register a new contest participant."""
    # Check if email or GitHub username already registered
    existing = (
        db.query(Participant)
        .filter(
            (Participant.email == registration.email) | (Participant.github_username == registration.github_username)
        )
        .first()
    )

    if existing:
        raise HTTPException(status_code=400, detail="Email or GitHub username already registered")

    # Create new participant
    participant = Participant(
        id=str(uuid.uuid4()),
        name=registration.name,
        email=registration.email,
        github_username=registration.github_username,
        category=registration.category,
        idea_description=registration.idea_description,
    )

    db.add(participant)

    try:
        db.commit()
        # Send confirmation email
        await send_registration_confirmation(registration.email, registration.name, participant.id)
        return {"id": participant.id, "status": "registered"}
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Registration failed")


@app.post("/submit")
async def submit_project(submission: Submission, db: Session = Depends(get_db)):
    """Submit a contest entry."""
    participant = db.query(Participant).filter(Participant.id == submission.participant_id).first()

    if not participant:
        raise HTTPException(status_code=404, detail="Participant not found")

    if participant.submission_url:
        raise HTTPException(status_code=400, detail="Project already submitted")

    # Verify GitHub repository
    if not verify_github_repo(submission.repository_url, os.getenv("GITHUB_TOKEN")):
        raise HTTPException(status_code=400, detail="Invalid repository or missing required files")

    # Update participant record
    participant.submission_url = submission.repository_url
    participant.submission_date = datetime.utcnow()

    try:
        db.commit()
        # Send confirmation
        await send_submission_confirmation(participant.email, participant.name)
        return {"status": "submitted"}
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Submission failed")


@app.get("/status/{participant_id}")
async def get_status(participant_id: str, db: Session = Depends(get_db)):
    """Get participant status and submission details."""
    participant = db.query(Participant).filter(Participant.id == participant_id).first()

    if not participant:
        raise HTTPException(status_code=404, detail="Participant not found")

    return {
        "name": participant.name,
        "category": participant.category,
        "registered_at": participant.registered_at,
        "submission_status": "submitted" if participant.submission_url else "pending",
        "submission_date": participant.submission_date,
        "judging_status": "complete" if participant.judging_complete else "pending",
    }


@app.get("/submissions")
async def list_submissions(category: Optional[str] = None, db: Session = Depends(get_db)):
    """List all contest submissions, optionally filtered by category."""
    query = db.query(Participant).filter(Participant.submission_url != None)

    if category:
        query = query.filter(Participant.category == category)

    submissions = query.all()
    return [
        {
            "id": s.id,
            "name": s.name,
            "category": s.category,
            "submission_date": s.submission_date,
            "repository_url": s.submission_url,
            "judging_complete": s.judging_complete,
        }
        for s in submissions
    ]


@app.get("/statistics")
async def get_statistics(db: Session = Depends(get_db)):
    """Get contest statistics."""
    total_registered = db.query(Participant).count()
    total_submitted = db.query(Participant).filter(Participant.submission_url != None).count()

    by_category = db.query(Participant.category, func.count(Participant.id)).group_by(Participant.category).all()

    return {
        "total_registered": total_registered,
        "total_submitted": total_submitted,
        "by_category": dict(by_category),
    }
