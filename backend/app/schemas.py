from typing import Optional, List
from pydantic import BaseModel

class TranslationRequest(BaseModel):
    text: str
    source_language: str = "Hindi"  # Hindi, Santhali, Mundari, Ho
    target_language: str = "Santhali"
    mode: str = "teacher"  # teacher (Hindi->Tribal) or student (Tribal->Hindi)

class TranslationResponse(BaseModel):
    source_text: str
    source_language: str
    target_language: str
    translated_text_devanagari: str
    translated_text_olchiki: Optional[str] = None
    phonetic_pronunciation: Optional[str] = None
    confidence_score: float
    needs_review: bool
    audio_url: Optional[str] = None
    source_audio_url: Optional[str] = None
    latency_ms: float
    is_offline_cached: bool = True

class TeacherFeedbackRequest(BaseModel):
    source_text: str
    ai_output: str
    corrected_text: str
    target_language: str = "Santhali"
    notes: Optional[str] = None

class TeacherFeedbackResponse(BaseModel):
    status: str
    message: str
    phrase_id: int

class FLNPhraseItem(BaseModel):
    id: int
    category: str
    hindi: str
    santhali_devanagari: str
    santhali_olchiki: Optional[str] = None
    santhali_phonetic: Optional[str] = None
    mundari: Optional[str] = None
    ho: Optional[str] = None
    english: Optional[str] = None
    audio_file: Optional[str] = None

class WorksheetRequest(BaseModel):
    topic: str = "Numeracy"  # Numeracy, Literacy, Colors, Animals, Classroom
    grade: str = "Grade 1"
    language: str = "Santhali"
    include_olchiki: bool = True
