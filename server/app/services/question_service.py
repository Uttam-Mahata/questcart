from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from fastapi import UploadFile, HTTPException, status
import json

from app.repositories.exam_repository import ExamRepository
from app.repositories.question_repository import QuestionRepository
from app.services.gemini_service import GeminiService
from app.utils.azure_storage_utils import AzureStorageService
from app.models.models import Section, QuestionType
from app.schemas.schemas import QuestionUnion, QuestionUpdate


class QuestionService:
    def __init__(self):
        self.exam_repository = ExamRepository()
        self.question_repository = QuestionRepository()
        self.gemini_service = GeminiService()
        self.azure_storage_service = AzureStorageService()
    
    def generate_questions_for_section(self, db: Session, section_id: int) -> List[QuestionUnion]:
        """Generate questions for a section and save them to the database"""
        # Get section details
        section = self.exam_repository.get_section(db, section_id)
        if not section:
            raise ValueError(f"Section with ID {section_id} not found")
        
        # Check if questions already exist for this section
        if self.question_repository.check_questions_exist(db, section_id):
            raise ValueError(f"Questions already exist for section with ID {section_id}")
        
        # Generate questions using Gemini
        questions = self.gemini_service.generate_questions(section)
        
        # Save questions to database
        self.question_repository.add_questions(db, section_id, questions)
        
        return questions
    
    def get_questions_for_section(self, db: Session, section_id: int):
        """Get already generated questions for a section"""
        # Check if section exists
        section = self.exam_repository.get_section(db, section_id)
        if not section:
            raise ValueError(f"Section with ID {section_id} not found")
            
        return self.question_repository.get_questions_by_section(db, section_id)
    
    def get_question(self, db: Session, question_id: int):
        """Get a question by ID"""
        question = self.question_repository.get_question(db, question_id)
        if not question:
            raise ValueError(f"Question with ID {question_id} not found")
        
        return question
    
    def update_question(self, db: Session, question_id: int, question_update: QuestionUpdate):
        """Update a question's content"""
        # Check if question exists
        question = self.question_repository.get_question(db, question_id)
        if not question:
            raise ValueError(f"Question with ID {question_id} not found")
        
        # Update the question
        updated_question = self.question_repository.update_question(db, question_id, question_update)
        
        return updated_question
    
    async def upload_question_image(self, db: Session, question_id: int, file: UploadFile):
        """Upload an image for a question and update the question's image URL"""
        # Check if question exists
        question = self.question_repository.get_question(db, question_id)
        if not question:
            raise ValueError(f"Question with ID {question_id} not found")
        
        # Check if the file is an image
        content_type = file.content_type
        if not content_type or not content_type.startswith('image/'):
            raise ValueError("File must be an image")
        
        try:
            # Upload the image to Azure Storage
            image_url = await self.azure_storage_service.upload_image(
                file, 
                folder=f"questions/{question.section_id}"
            )
            
            # If the question already has an image, delete the old one
            if question.image_url:
                self.azure_storage_service.delete_image(question.image_url)
            
            # Update the question with the new image URL
            updated_question = self.question_repository.update_question_image(db, question_id, image_url)
            
            return {"image_url": image_url}
        except Exception as e:
            raise ValueError(f"Failed to upload image: {str(e)}")
    
    async def upload_option_image(self, file: UploadFile, section_id: int):
        """Upload an image for an option and return the URL"""
        # Check if the file is an image
        content_type = file.content_type
        if not content_type or not content_type.startswith('image/'):
            raise ValueError("File must be an image")
        
        try:
            # Upload the image to Azure Storage
            image_url = await self.azure_storage_service.upload_image(
                file, 
                folder=f"options/{section_id}"
            )
            
            return {"image_url": image_url}
        except Exception as e:
            raise ValueError(f"Failed to upload image: {str(e)}")