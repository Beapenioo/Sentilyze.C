from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List

class UserBase(BaseModel):
    name: str
    surname: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    user_id: int
    created_at: datetime
    is_admin: bool

    class Config:
        from_attributes = True

class SettingsBase(BaseModel):
    theme: str
    language: str
    notifications_enabled: bool

class SettingsCreate(SettingsBase):
    user_id: int

class SettingsResponse(SettingsBase):
    setting_id: int

    class Config:
        from_attributes = True

class TextEntryBase(BaseModel):
    text_content: str

class TextEntryCreate(TextEntryBase):
    user_id: int

class TextEntryResponse(TextEntryBase):
    text_id: int
    timestamp: datetime

    class Config:
        from_attributes = True

class AnalysisResultBase(BaseModel):
    sentiment: str
    sentiment_score: float

class AnalysisResultCreate(AnalysisResultBase):
    text_id: int

class AnalysisResultResponse(AnalysisResultBase):
    result_id: int
    analysis_date: datetime

    class Config:
        from_attributes = True

class FeedbackBase(BaseModel):
    feedback_text: Optional[str] = None
    rating: int

class FeedbackCreate(FeedbackBase):
    user_id: int
    text_id: int

class FeedbackResponse(FeedbackBase):
    feedback_id: int
    feedback_date: datetime

    class Config:
        from_attributes = True

class SessionLogBase(BaseModel):
    user_id: int
    login_time: datetime
    logout_time: Optional[datetime] = None

class SessionLogCreate(SessionLogBase):
    pass

class SessionLogResponse(SessionLogBase):
    session_id: int

    class Config:
        from_attributes = True 