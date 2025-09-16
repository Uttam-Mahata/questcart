from pydantic import BaseModel, Field
from typing import List, Optional, Union, Literal, Dict, Any
from datetime import datetime
from enum import Enum

class QuestionType(str, Enum):
    MCQ = "MCQ"
    MSQ = "MSQ"
    NUM = "NUM"

# Section Schema for creating exams
class SectionCreate(BaseModel):
    name: str
    topics: Optional[str] = None
    syllabus_file_uri: Optional[str] = None
    total_questions: int
    questions_to_attempt: int
    marks_per_question: float
    negative_marking_allowed: bool = False
    negative_marks: Optional[float] = None
    question_type: QuestionType

# Exam Creation Schema
class ExamCreate(BaseModel):
    name: str
    time_minutes: int
    sections: List[SectionCreate]

# Section Response Schema
class SectionResponse(SectionCreate):
    id: int
    exam_id: int
    
    class Config:
        from_attributes = True

# Exam Response Schema
class ExamResponse(BaseModel):
    id: int
    name: str
    total_marks: float
    time_minutes: int
    created_at: str
    sections: List[SectionResponse]
    
    class Config:
        from_attributes = True

# Option for MCQ/MSQ Questions
class Option(BaseModel):
    text: str
    is_correct: bool
    image_url: Optional[str] = None

# Base Question Schema for Gemini API's structured response
class QuestionBase(BaseModel):
    question_text: str
    explanation: Optional[str] = None
    image_url: Optional[str] = None

# MCQ Question Schema
class MCQQuestion(QuestionBase):
    options: List[Option]

# MSQ Question Schema
class MSQQuestion(QuestionBase):
    options: List[Option]

# Numerical Question Schema
class NumericalQuestion(QuestionBase):
    answer: float
    
# Union Type for different question types
QuestionUnion = Union[MCQQuestion, MSQQuestion, NumericalQuestion]

# Request to generate questions for a section
class GenerateQuestionsRequest(BaseModel):
    section_id: int

# Response for generated questions
class GeneratedQuestionResponse(BaseModel):
    section_id: int
    questions: List[QuestionUnion]
    
# DB Question Schema
class QuestionResponse(BaseModel):
    id: int
    section_id: int
    question_text: str
    question_type: QuestionType
    options: Optional[str] = None
    correct_answer: Optional[str] = None
    numerical_answer: Optional[float] = None
    image_url: Optional[str] = None
    last_modified: Optional[str] = None
    
    class Config:
        from_attributes = True

# Schema for question update
class QuestionUpdate(BaseModel):
    question_text: Optional[str] = None
    options: Optional[List[Option]] = None
    numerical_answer: Optional[float] = None
    
# Schema for image upload response
class ImageUploadResponse(BaseModel):
    image_url: str
    
# Schema for question image update
class QuestionImageUpdate(BaseModel):
    image_url: str

# Schema for syllabus upload response
class SyllabusUploadResponse(BaseModel):
    file_uri: str