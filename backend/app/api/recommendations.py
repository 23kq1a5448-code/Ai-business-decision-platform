from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.database import get_db
from app.models.recommendation import Recommendation, RecommendationStatus, ImpactCategory
from app.schemas.recommendation import RecommendationCreate, RecommendationUpdate, RecommendationResponse
from app.core.deps import get_current_user, get_current_business
from app.models.user import User

router = APIRouter()


@router.post("/", response_model=RecommendationResponse)
def create_recommendation(
    recommendation_data: RecommendationCreate,
    current_business = Depends(get_current_business),
    db: Session = Depends(get_db)
):
    """Create a new recommendation."""
    new_recommendation = Recommendation(
        business_id=current_business.id,
        **recommendation_data.model_dump()
    )
    db.add(new_recommendation)
    db.commit()
    db.refresh(new_recommendation)
    return RecommendationResponse.model_validate(new_recommendation)


@router.get("/", response_model=List[RecommendationResponse])
def get_recommendations(
    skip: int = 0,
    limit: int = 100,
    status: Optional[RecommendationStatus] = None,
    impact_category: Optional[ImpactCategory] = None,
    current_business = Depends(get_current_business),
    db: Session = Depends(get_db)
):
    """Get recommendations with filtering."""
    query = db.query(Recommendation).filter(Recommendation.business_id == current_business.id)

    if status:
        query = query.filter(Recommendation.status == status)
    if impact_category:
        query = query.filter(Recommendation.impact_category == impact_category)

    recommendations = query.order_by(Recommendation.created_at.desc()).offset(skip).limit(limit).all()
    return [RecommendationResponse.model_validate(rec) for rec in recommendations]


@router.get("/{recommendation_id}", response_model=RecommendationResponse)
def get_recommendation(
    recommendation_id: int,
    current_business = Depends(get_current_business),
    db: Session = Depends(get_db)
):
    """Get a specific recommendation by ID."""
    recommendation = db.query(Recommendation).filter(
        Recommendation.id == recommendation_id,
        Recommendation.business_id == current_business.id
    ).first()
    if not recommendation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recommendation not found"
        )
    return RecommendationResponse.model_validate(recommendation)


@router.put("/{recommendation_id}", response_model=RecommendationResponse)
def update_recommendation(
    recommendation_id: int,
    recommendation_data: RecommendationUpdate,
    current_business = Depends(get_current_business),
    db: Session = Depends(get_db)
):
    """Update a recommendation (typically status)."""
    recommendation = db.query(Recommendation).filter(
        Recommendation.id == recommendation_id,
        Recommendation.business_id == current_business.id
    ).first()
    if not recommendation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recommendation not found"
        )

    update_data = recommendation_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(recommendation, field, value)

    # Set completed_at if status is being set to completed
    if update_data.get("status") == RecommendationStatus.COMPLETED:
        from datetime import datetime
        recommendation.completed_at = datetime.utcnow()

    db.commit()
    db.refresh(recommendation)
    return RecommendationResponse.model_validate(recommendation)


@router.delete("/{recommendation_id}")
def delete_recommendation(
    recommendation_id: int,
    current_business = Depends(get_current_business),
    db: Session = Depends(get_db)
):
    """Delete a recommendation."""
    recommendation = db.query(Recommendation).filter(
        Recommendation.id == recommendation_id,
        Recommendation.business_id == current_business.id
    ).first()
    if not recommendation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recommendation not found"
        )

    db.delete(recommendation)
    db.commit()

    return {"message": "Recommendation deleted successfully"}
