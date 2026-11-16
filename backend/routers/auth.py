"""Authentication routes: register and login."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database.connection import get_db
from models.user import User, UserRole
from models.candidate import Candidate
from models.recruiter import Recruiter
from schemas.schemas import UserRegister, UserLogin, Token
from auth.jwt_handler import (
    get_password_hash,
    verify_password,
    create_access_token,
)

router = APIRouter(tags=["Authentication"])


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """Register a new user as recruiter or candidate."""
    existing = db.query(User).filter(User.email == user_data.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    role = UserRole.RECRUITER if user_data.role == "recruiter" else UserRole.CANDIDATE

    user = User(
        email=user_data.email,
        password_hash=get_password_hash(user_data.password),
        role=role,
    )
    db.add(user)
    db.flush()

    if role == UserRole.CANDIDATE:
        candidate = Candidate(user_id=user.id, name=user_data.name or "")
        db.add(candidate)
    else:
        recruiter = Recruiter(user_id=user.id, company=user_data.company or "")
        db.add(recruiter)

    db.commit()
    db.refresh(user)

    token = create_access_token(data={"sub": str(user.id), "role": user.role.value})
    return Token(
        access_token=token,
        role=user.role.value,
        user_id=user.id,
    )


@router.post("/login", response_model=Token)
async def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """Authenticate user and return JWT token."""
    user = db.query(User).filter(User.email == credentials.email).first()
    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    token = create_access_token(data={"sub": str(user.id), "role": user.role.value})
    return Token(
        access_token=token,
        role=user.role.value,
        user_id=user.id,
    )
