from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.models.business import Business, BusinessMembership, MembershipRole
from app.schemas.business import BusinessCreate, BusinessResponse, BusinessMembershipCreate
from app.core.deps import get_current_user, get_current_business
from app.models.user import User

router = APIRouter()


@router.post("/", response_model=BusinessResponse)
def create_business(
    business_data: BusinessCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new business."""
    new_business = Business(**business_data.model_dump())
    db.add(new_business)
    db.flush()

    # Add user as owner
    membership = BusinessMembership(
        user_id=current_user.id,
        business_id=new_business.id,
        role=MembershipRole.OWNER
    )
    db.add(membership)
    db.commit()
    db.refresh(new_business)

    return BusinessResponse.model_validate(new_business)


@router.get("/", response_model=List[BusinessResponse])
def get_user_businesses(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all businesses for the current user."""
    memberships = db.query(BusinessMembership).filter(
        BusinessMembership.user_id == current_user.id
    ).all()

    business_ids = [m.business_id for m in memberships]
    businesses = db.query(Business).filter(Business.id.in_(business_ids)).all()

    return [BusinessResponse.model_validate(b) for b in businesses]


@router.get("/current", response_model=BusinessResponse)
def get_current_business_info(
    current_business: Business = Depends(get_current_business)
):
    """Get the current active business."""
    return BusinessResponse.model_validate(current_business)


@router.post("/{business_id}/join", response_model=BusinessResponse)
def join_business(
    business_id: int,
    membership_data: BusinessMembershipCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Join an existing business (requires invitation/approval in production)."""
    business = db.query(Business).filter(Business.id == business_id).first()
    if not business:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business not found"
        )

    # Check if already a member
    existing = db.query(BusinessMembership).filter(
        BusinessMembership.user_id == current_user.id,
        BusinessMembership.business_id == business_id
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already a member of this business"
        )

    membership = BusinessMembership(
        user_id=current_user.id,
        business_id=business_id,
        role=membership_data.role
    )
    db.add(membership)
    db.commit()

    return BusinessResponse.model_validate(business)
