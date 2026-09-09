import datetime
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, Boolean
from .database import Base

class VerifiedPhrase(Base):
    __tablename__ = "verified_phrases"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(String(100), index=True)
    source_lang = Column(String(50), default="Hindi")
    target_lang = Column(String(50), default="Santhali")
    source_text = Column(Text, nullable=False)
    translated_devanagari = Column(Text, nullable=False)
    translated_olchiki = Column(Text, nullable=True)
    phonetic = Column(Text, nullable=True)
    audio_path = Column(String(255), nullable=True)
    confidence = Column(Float, default=1.0)
    is_verified = Column(Boolean, default=True)
    verified_by = Column(String(100), default="Teacher")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class TeacherCorrection(Base):
    __tablename__ = "teacher_corrections"

    id = Column(Integer, primary_key=True, index=True)
    source_text = Column(Text, nullable=False)
    original_ai_output = Column(Text, nullable=False)
    teacher_corrected_text = Column(Text, nullable=False)
    target_language = Column(String(50), default="Santhali")
    feedback_notes = Column(String(255), nullable=True)
    approved = Column(Boolean, default=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

class LessonPack(Base):
    __tablename__ = "lesson_packs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(150), nullable=False)
    grade = Column(String(20), default="Primary Grade 1-3")
    subject = Column(String(50), default="Foundational Literacy & Numeracy")
    language = Column(String(50), default="Santhali")
    content_json = Column(Text, nullable=False)
    is_cached_offline = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
