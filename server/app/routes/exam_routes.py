from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.schemas.schemas import (
    ExamCreate, ExamResponse, GenerateQuestionsRequest, GeneratedQuestionResponse, 
    QuestionResponse, QuestionUpdate, ImageUploadResponse, SyllabusUploadResponse
)
from app.repositories.exam_repository import ExamRepository
from app.services.question_service import QuestionService
from app.services.section_service import SectionService
import json

router = APIRouter(prefix="/api/exams", tags=["exams"])
exam_repository = ExamRepository()
question_service = QuestionService()
section_service = SectionService()


@router.post("/", response_model=ExamResponse, status_code=status.HTTP_201_CREATED)
def create_exam(exam: ExamCreate, db: Session = Depends(get_db)):
    """Create a new exam with sections"""
    try:
        db_exam = exam_repository.create_exam(db, exam)
        return db_exam
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{exam_id}", response_model=ExamResponse)
def get_exam(exam_id: int, db: Session = Depends(get_db)):
    """Get exam details by ID"""
    db_exam = exam_repository.get_exam(db, exam_id)
    if db_exam is None:
        raise HTTPException(status_code=404, detail=f"Exam with ID {exam_id} not found")
    return db_exam


@router.get("/", response_model=List[ExamResponse])
def get_all_exams(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all exams with pagination"""
    exams = exam_repository.get_all_exams(db, skip=skip, limit=limit)
    return exams


@router.post("/sections/{section_id}/generate-questions", status_code=status.HTTP_201_CREATED)
def generate_questions(section_id: int, db: Session = Depends(get_db)):
    """Generate questions for a specific section"""
    try:
        # Check if section exists
        section = exam_repository.get_section(db, section_id)
        if not section:
            raise HTTPException(status_code=404, detail=f"Section with ID {section_id} not found")
        
        # Generate questions
        question_service.generate_questions_for_section(db, section_id)
        
        return {"message": f"Questions generated successfully for section {section_id}"}
    except ValueError as e:
        if "already exist" in str(e):
            raise HTTPException(status_code=400, detail=str(e))
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        # Log the full exception for debugging
        import traceback
        error_details = f"Failed to generate questions: {str(e)}\n{traceback.format_exc()}"
        print(error_details)  # This will show in server logs
        
        if "GEMINI_API_KEY" in str(e) or "API key" in str(e):
            raise HTTPException(
                status_code=500, 
                detail=f"Gemini API key configuration error: Please check that the GEMINI_API_KEY environment variable is set properly."
            )
        else:
            raise HTTPException(status_code=500, detail=f"Failed to generate questions: {str(e)}")


@router.get("/sections/{section_id}/questions", response_model=List[QuestionResponse])
def get_section_questions(section_id: int, db: Session = Depends(get_db)):
    """Get all questions for a specific section"""
    try:
        questions = question_service.get_questions_for_section(db, section_id)
        return questions
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# New endpoints for question management and image upload

@router.get("/questions/{question_id}", response_model=QuestionResponse)
def get_question(question_id: int, db: Session = Depends(get_db)):
    """Get a specific question by ID"""
    try:
        question = question_service.get_question(db, question_id)
        return question
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/questions/{question_id}", response_model=QuestionResponse)
def update_question(question_id: int, question_update: QuestionUpdate, db: Session = Depends(get_db)):
    """Update a question's content"""
    try:
        updated_question = question_service.update_question(db, question_id, question_update)
        return updated_question
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/questions/{question_id}/upload-image", response_model=ImageUploadResponse)
async def upload_question_image(
    question_id: int, 
    file: UploadFile = File(...), 
    db: Session = Depends(get_db)
):
    """Upload an image for a question"""
    try:
        result = await question_service.upload_question_image(db, question_id, file)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sections/{section_id}/upload-option-image", response_model=ImageUploadResponse)
async def upload_option_image(
    section_id: int, 
    file: UploadFile = File(...), 
    db: Session = Depends(get_db)
):
    """Upload an image for a question option"""
    try:
        # Verify section exists
        section = exam_repository.get_section(db, section_id)
        if not section:
            raise HTTPException(status_code=404, detail=f"Section with ID {section_id} not found")
        
        # Upload the image
        result = await question_service.upload_option_image(file, section_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sections/{section_id}/upload-syllabus", response_model=SyllabusUploadResponse)
async def upload_syllabus(
    section_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload a syllabus PDF for a section"""
    try:
        result = await section_service.upload_syllabus(db, section_id, file)
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        # Log the error for debugging
        print(f"Error in upload_syllabus endpoint: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred during syllabus upload.")