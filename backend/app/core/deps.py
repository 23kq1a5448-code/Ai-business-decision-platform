from typing import Optional, Generator
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.core.security import decode_access_token
from app.models.user import User, UserRole
from app.models.business import Business, BusinessMembership, MembershipRole

security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get the current authenticated user from JWT token."""
    token = credentials.credentials
    payload = decode_access_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id: int = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )

    return user


def get_current_business(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Business:
    """Get the current user's active business (simplified: first business)."""
    membership = db.query(BusinessMembership).filter(
        BusinessMembership.user_id == current_user.id
    ).first()

    if membership is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No business found for user"
        )

    business = db.query(Business).filter(Business.id == membership.business_id).first()
    if business is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business not found"
        )

    return business


def require_role(required_roles: list[UserRole]):
    """Dependency factory to require specific user roles."""
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required roles: {[r.value for r in required_roles]}"
            )
        return current_user
    return role_checker


def require_business_role(required_roles: list[MembershipRole]):
    """Dependency factory to require specific business membership roles."""
    def role_checker(
        current_user: User = Depends(get_current_user),
        current_business: Business = Depends(get_current_business),
        db: Session = Depends(get_db)
    ) -> User:
        membership = db.query(BusinessMembership).filter(
            BusinessMembership.user_id == current_user.id,
            BusinessMembership.business_id == current_business.id
        ).first()

        if membership is None or membership.role not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient business permissions. Required roles: {[r.value for r in required_roles]}"
            )

        return current_user
    return role_checker
