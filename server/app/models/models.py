from sqlalchemy import Column, Integer, String, Float, ForeignKey, Boolean, Text, Enum
from sqlalchemy.orm import relationship
import enum
from app.core.database import Base

class QuestionType(enum.Enum):
    MCQ = "MCQ"  # Multiple Choice Question
    MSQ = "MSQ"  # Multiple Select Question
    NUM = "NUM"  # Numerical

class Exam(Base):
    __tablename__ = "exams"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True)  # Added length constraint
    total_marks = Column(Float)
    time_minutes = Column(Integer)
    created_at = Column(String(50))  # Added length constraint
    
    # Relationship
    sections = relationship("Section", back_populates="exam", cascade="all, delete-orphan")

class Section(Base):
    __tablename__ = "sections"

    id = Column(Integer, primary_key=True, index=True)
    exam_id = Column(Integer, ForeignKey("exams.id"))
    name = Column(String(255))  # Added length constraint
    topics = Column(Text, nullable=True)
    syllabus_file_uri = Column(String(1024), nullable=True)
    total_questions = Column(Integer)
    questions_to_attempt = Column(Integer)
    marks_per_question = Column(Float)
    negative_marking_allowed = Column(Boolean, default=False)
    negative_marks = Column(Float, nullable=True)
    question_type = Column(Enum(QuestionType))
    
    # Relationships
    exam = relationship("Exam", back_populates="sections")
    questions = relationship("Question", back_populates="section", cascade="all, delete-orphan")

class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    section_id = Column(Integer, ForeignKey("sections.id"))
    question_text = Column(Text)
    question_type = Column(Enum(QuestionType))
    
    # New field for question image
    image_url = Column(String(1024), nullable=True)  # Added length constraint
    
    # For MCQ/MSQ
    options = Column(Text, nullable=True)  # JSON string containing options with possible image URLs
    correct_answer = Column(Text, nullable=True)  # Could be index(es) or values for different question types
    
    # For numerical
    numerical_answer = Column(Float, nullable=True)
    
    # Last modified timestamp
    last_modified = Column(String(50), nullable=True)  # Added length constraint
    
    # Relationship
    section = relationship("Section", back_populates="questions")