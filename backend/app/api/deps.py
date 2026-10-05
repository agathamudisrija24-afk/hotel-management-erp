from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.security import decode
from app.models.models import User, UserRole, Role
bearer=HTTPBearer(auto_error=False)
def current_user(credentials: HTTPAuthorizationCredentials=Depends(bearer), db: Session=Depends(get_db)):
    if not credentials: raise HTTPException(status.HTTP_401_UNAUTHORIZED,"Authentication required")
    data=decode(credentials.credentials); user=db.get(User,data["sub"])
    if not user or not user.active: raise HTTPException(status.HTTP_401_UNAUTHORIZED,"User unavailable")
    return user
def optional_current_user(credentials: HTTPAuthorizationCredentials | None=Depends(bearer), db: Session=Depends(get_db)):
    if not credentials: return None
    data=decode(credentials.credentials); user=db.get(User,data["sub"])
    if not user or not user.active: raise HTTPException(status.HTTP_401_UNAUTHORIZED,"User unavailable")
    return user
def require(*allowed):
    def check(user=Depends(current_user),db: Session=Depends(get_db)):
        roles=[r.name for r in db.query(Role).join(UserRole).filter(UserRole.user_id==user.id).all()]
        if not set(roles)&set(allowed): raise HTTPException(403,"Insufficient permission")
        return user
    return check

def can_access_hotel(db: Session, user: User, hotel_id: str, allowed: set[str]) -> bool:
    """Explicitly scope staff actions to a hotel assignment; admins remain global."""
    rows = db.query(Role.name, UserRole.hotel_id).join(UserRole).filter(UserRole.user_id == user.id).all()
    return any(name == "admin" or (name in allowed and assigned_hotel == hotel_id) for name, assigned_hotel in rows)
