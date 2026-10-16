from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.database import get_db
from app.models.chat import ChatSession, ChatMessage, MessageRole
from app.schemas.chat import ChatSessionCreate, ChatSessionResponse, ChatMessageCreate, ChatMessageResponse
from app.core.deps import get_current_user, get_current_business
from app.models.user import User
import pandas as pd
import io

router = APIRouter()


@router.post("/sessions/", response_model=ChatSessionResponse)
def create_chat_session(
    session_data: ChatSessionCreate,
    current_user: User = Depends(get_current_user),
    current_business = Depends(get_current_business),
    db: Session = Depends(get_db)
):
    """Create a new chat session."""
    new_session = ChatSession(
        business_id=current_business.id,
        user_id=current_user.id,
        session_name=session_data.session_name
    )
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    return ChatSessionResponse.model_validate(new_session)


@router.get("/sessions/", response_model=List[ChatSessionResponse])
def get_chat_sessions(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    current_business = Depends(get_current_business),
    db: Session = Depends(get_db)
):
    """Get chat sessions for the current user."""
    sessions = db.query(ChatSession).filter(
        ChatSession.business_id == current_business.id,
        ChatSession.user_id == current_user.id
    ).order_by(ChatSession.updated_at.desc()).offset(skip).limit(limit).all()
    return [ChatSessionResponse.model_validate(session) for session in sessions]


@router.get("/sessions/{session_id}", response_model=ChatSessionResponse)
def get_chat_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    current_business = Depends(get_current_business),
    db: Session = Depends(get_db)
):
    """Get a specific chat session."""
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.business_id == current_business.id,
        ChatSession.user_id == current_user.id
    ).first()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found"
        )
    return ChatSessionResponse.model_validate(session)


@router.get("/sessions/{session_id}/messages", response_model=List[ChatMessageResponse])
def get_chat_messages(
    session_id: int,
    current_user: User = Depends(get_current_user),
    current_business = Depends(get_current_business),
    db: Session = Depends(get_db)
):
    """Get messages for a chat session."""
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.business_id == current_business.id,
        ChatSession.user_id == current_user.id
    ).first()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found"
        )

    messages = db.query(ChatMessage).filter(
        ChatMessage.session_id == session_id
    ).order_by(ChatMessage.created_at).all()
    return [ChatMessageResponse.model_validate(msg) for msg in messages]


@router.post("/sessions/{session_id}/messages", response_model=ChatMessageResponse)
def create_chat_message(
    session_id: int,
    message_data: ChatMessageCreate,
    current_user: User = Depends(get_current_user),
    current_business = Depends(get_current_business),
    db: Session = Depends(get_db)
):
    """Create a new chat message and generate AI response."""
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.business_id == current_business.id,
        ChatSession.user_id == current_user.id
    ).first()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found"
        )

    # Create user message
    user_message = ChatMessage(
        session_id=session_id,
        role=message_data.role,
        content=message_data.content,
        message_metadata=message_data.message_metadata
    )
    db.add(user_message)
    db.flush()

    # Generate AI response (rule-based for now, will be enhanced with LLM in Stage 5)
    ai_response_content = generate_ai_response(message_data.content, current_business, db)

    ai_message = ChatMessage(
        session_id=session_id,
        role=MessageRole.ASSISTANT,
        content=ai_response_content,
        message_metadata={"source": "rule_based"}
    )
    db.add(ai_message)

    # Update session timestamp
    from datetime import datetime
    session.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(ai_message)
    return ChatMessageResponse.model_validate(ai_message)


@router.post("/upload-csv")
async def upload_csv(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    current_business = Depends(get_current_business),
    db: Session = Depends(get_db)
):
    """Upload a CSV file for data analysis."""
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only CSV files are supported"
        )

    try:
        contents = await file.read()
        df = pd.read_csv(io.BytesIO(contents))

        # Basic analysis
        analysis = {
            "filename": file.filename,
            "rows": len(df),
            "columns": list(df.columns),
            "column_types": {col: str(df[col].dtype) for col in df.columns},
            "sample_data": df.head(5).to_dict(orient="records"),
            "summary": df.describe().to_dict() if len(df.select_dtypes(include=['number']).columns) > 0 else {}
        }

        return {
            "message": "File uploaded successfully",
            "analysis": analysis
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error processing CSV file: {str(e)}"
        )


def generate_ai_response(question: str, business, db: Session) -> str:
    """Generate AI response using rule-based logic (will be enhanced with LLM)."""
    from app.models.sale import Sale, SaleItem
    from app.models.product import Product
    from app.models.customer import Customer
    from sqlalchemy import func

    question_lower = question.lower()

    # Sales-related queries
    if "total sales" in question_lower or "revenue" in question_lower:
        total_sales = db.query(func.sum(Sale.total_amount)).filter(
            Sale.business_id == business.id,
            Sale.status == "completed"
        ).scalar() or 0
        return f"Your total sales are ${total_sales:,.2f}."

    if "products" in question_lower and "profit" in question_lower:
        top_products = db.query(
            Product.name,
            func.sum(SaleItem.total_profit).label('total_profit')
        ).join(
            SaleItem, Product.id == SaleItem.product_id
        ).join(
            Sale, SaleItem.sale_id == Sale.id
        ).filter(
            Sale.business_id == business.id,
            Sale.status == "completed"
        ).group_by(Product.id, Product.name).order_by(
            func.sum(SaleItem.total_profit).desc()
        ).limit(5).all()

        if top_products:
            response = "Top products by profit:\n"
            for p in top_products:
                response += f"- {p.name}: ${p.total_profit:,.2f}\n"
            return response
        return "No sales data available yet."

    if "churn" in question_lower:
        high_risk_customers = db.query(Customer).filter(
            Customer.business_id == business.id,
            Customer.churn_risk == "high"
        ).count()
        return f"There are {high_risk_customers} customers at high risk of churning."

    if "stock" in question_lower or "inventory" in question_lower:
        low_stock = db.query(Product).filter(
            Product.business_id == business.id,
            Product.stock_quantity <= Product.low_stock_threshold
        ).count()
        return f"There are {low_stock} products with low stock that need replenishment."

    if "customers" in question_lower:
        total_customers = db.query(func.count(Customer.id)).filter(
            Customer.business_id == business.id
        ).scalar() or 0
        return f"You have {total_customers} customers in your database."

    # Default response
    return "I can help you analyze your business data. Try asking about total sales, product profitability, customer churn risk, inventory levels, or customer count. For more advanced analysis, please configure an LLM API key in the backend environment."
