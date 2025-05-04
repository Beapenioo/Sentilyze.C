from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Float, Text
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    surname = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_admin = Column(Boolean, default=False)
    settings = relationship("Settings", uselist=False, back_populates="user")
    text_entries = relationship("TextEntry", back_populates="user")
    feedbacks = relationship("Feedback", back_populates="user")
    sessions = relationship("SessionLogs", back_populates="user")

class Settings(Base):
    __tablename__ = "settings"
    setting_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), unique=True)
    theme = Column(String(50))
    language = Column(String(50))
    notifications_enabled = Column(Boolean, default=True)
    user = relationship("User", back_populates="settings")

class TextEntry(Base):
    __tablename__ = "text_entries"
    text_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    text_content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    user = relationship("User", back_populates="text_entries")
    analysis_result = relationship("AnalysisResult", uselist=False, back_populates="text_entry")
    feedbacks = relationship("Feedback", back_populates="text_entry")

class AnalysisResult(Base):
    __tablename__ = "analysis_results"
    result_id = Column(Integer, primary_key=True, autoincrement=True)
    text_id = Column(Integer, ForeignKey("text_entries.text_id"))
    sentiment = Column(String(20))
    sentiment_score = Column(Float)
    analysis_date = Column(DateTime, default=datetime.utcnow)
    text_entry = relationship("TextEntry", back_populates="analysis_result")

class Feedback(Base):
    __tablename__ = "feedbacks"
    feedback_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    text_id = Column(Integer, ForeignKey("text_entries.text_id"))
    feedback_text = Column(Text)
    rating = Column(Integer)
    feedback_date = Column(DateTime, default=datetime.utcnow)
    user = relationship("User", back_populates="feedbacks")
    text_entry = relationship("TextEntry", back_populates="feedbacks")

class SessionLogs(Base):
    __tablename__ = "session_logs"
    session_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    login_time = Column(DateTime, default=datetime.utcnow)
    logout_time = Column(DateTime)
    user = relationship("User", back_populates="sessions") 