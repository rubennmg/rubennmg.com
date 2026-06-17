from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_session_token
from app.core.config import settings
from app.core.passwords import verify_password
from app.core.rate_limit import login_rate_limiter
from app.core.security import create_csrf_token, create_session_token
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import AuthUser, CsrfResponse, LoginRequest, LoginResponse

router = APIRouter(prefix="/api/auth", tags=["auth"])


def _login_rate_limit_key(request: Request, username: str) -> str:
    client_host = request.client.host if request.client else "unknown"
    return f"{client_host}:{username.lower()}"


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, request: Request, response: Response, db: Session = Depends(get_db)) -> LoginResponse:
    key = _login_rate_limit_key(request, payload.username)
    if login_rate_limiter.is_limited(key):
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Too many failed login attempts")

    user = db.scalar(select(User).where(User.username == payload.username, User.is_active.is_(True)))
    if user is None or not verify_password(payload.password, user.password_hash):
        login_rate_limiter.record_failure(key)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    login_rate_limiter.record_success(key)
    session_token = create_session_token(user.id, user.role)
    response.set_cookie(
        key=settings.auth_cookie_name,
        value=session_token,
        httponly=True,
        secure=settings.secure_cookies,
        samesite="lax",
        max_age=settings.auth_session_days * 24 * 60 * 60,
        path="/",
    )
    return LoginResponse(user=AuthUser.model_validate(user))


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(response: Response) -> None:
    response.delete_cookie(
        key=settings.auth_cookie_name,
        httponly=True,
        secure=settings.secure_cookies,
        samesite="lax",
        path="/",
    )


@router.get("/me", response_model=LoginResponse)
def me(current_user: User = Depends(get_current_user)) -> LoginResponse:
    return LoginResponse(user=AuthUser.model_validate(current_user))


@router.get("/csrf", response_model=CsrfResponse)
def csrf(session_token: str = Depends(get_session_token)) -> CsrfResponse:
    return CsrfResponse(csrf_token=create_csrf_token(session_token))
