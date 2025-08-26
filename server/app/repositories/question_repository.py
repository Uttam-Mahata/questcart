from sqlalchemy.orm import Session
import json
import datetime
from typing import List, Dict, Any, Optional
from app.models.models import Question, QuestionType, Section
from app.schemas.schemas import QuestionUnion, MCQQuestion, MSQQuestion, NumericalQuestion, QuestionUpdate, Option


class QuestionRepository:
    def add_questions(self, db: Session, section_id: int, questions: List[QuestionUnion]) -> List[Question]:
        section = db.query(Section).filter(Section.id == section_id).first()
        if not section:
            raise ValueError(f"Section with ID {section_id} not found")
        
        db_questions = []
        for question in questions:
            # Handle different question types
            if isinstance(question, MCQQuestion):
                options = [{"text": opt.text, "is_correct": opt.is_correct, "image_url": opt.image_url} for opt in question.options]
                correct_answers = [i for i, opt in enumerate(question.options) if opt.is_correct]
                
                db_question = Question(
                    section_id=section_id,
                    question_text=question.question_text,
                    question_type=QuestionType.MCQ,
                    options=json.dumps(options),
                    correct_answer=json.dumps(correct_answers),
                    image_url=question.image_url,
                    last_modified=datetime.datetime.now().isoformat()
                )
            
            elif isinstance(question, MSQQuestion):
                options = [{"text": opt.text, "is_correct": opt.is_correct, "image_url": opt.image_url} for opt in question.options]
                correct_answers = [i for i, opt in enumerate(question.options) if opt.is_correct]
                
                db_question = Question(
                    section_id=section_id,
                    question_text=question.question_text,
                    question_type=QuestionType.MSQ,
                    options=json.dumps(options),
                    correct_answer=json.dumps(correct_answers),
                    image_url=question.image_url,
                    last_modified=datetime.datetime.now().isoformat()
                )
            
            elif isinstance(question, NumericalQuestion):
                db_question = Question(
                    section_id=section_id,
                    question_text=question.question_text,
                    question_type=QuestionType.NUM,
                    numerical_answer=question.answer,
                    image_url=question.image_url,
                    last_modified=datetime.datetime.now().isoformat()
                )
            
            db.add(db_question)
            db_questions.append(db_question)
        
        db.commit()
        for question in db_questions:
            db.refresh(question)
        
        return db_questions
    
    def get_questions_by_section(self, db: Session, section_id: int) -> List[Question]:
        return db.query(Question).filter(Question.section_id == section_id).all()
    
    def check_questions_exist(self, db: Session, section_id: int) -> bool:
        """Check if questions already exist for a section"""
        count = db.query(Question).filter(Question.section_id == section_id).count()
        return count > 0
    
    def get_question(self, db: Session, question_id: int) -> Optional[Question]:
        """Get a question by ID"""
        return db.query(Question).filter(Question.id == question_id).first()
    
    def update_question(self, db: Session, question_id: int, question_update: QuestionUpdate) -> Optional[Question]:
        """Update a question's content"""
        db_question = db.query(Question).filter(Question.id == question_id).first()
        if not db_question:
            return None
        
        # Update question text if provided
        if question_update.question_text is not None:
            db_question.question_text = question_update.question_text
        
        # Update options if provided (for MCQ/MSQ)
        if question_update.options is not None and db_question.question_type in [QuestionType.MCQ, QuestionType.MSQ]:
            options = [{"text": opt.text, "is_correct": opt.is_correct, "image_url": opt.image_url} for opt in question_update.options]
            correct_answers = [i for i, opt in enumerate(question_update.options) if opt.is_correct]
            
            db_question.options = json.dumps(options)
            db_question.correct_answer = json.dumps(correct_answers)
        
        # Update numerical answer if provided (for NUM)
        if question_update.numerical_answer is not None and db_question.question_type == QuestionType.NUM:
            db_question.numerical_answer = question_update.numerical_answer
        
        # Update last modified timestamp
        db_question.last_modified = datetime.datetime.now().isoformat()
        
        db.commit()
        db.refresh(db_question)
        return db_question
    
    def update_question_image(self, db: Session, question_id: int, image_url: str) -> Optional[Question]:
        """Update a question's image URL"""
        db_question = db.query(Question).filter(Question.id == question_id).first()
        if not db_question:
            return None
        
        # Update image URL
        db_question.image_url = image_url
        
        # Update last modified timestamp
        db_question.last_modified = datetime.datetime.now().isoformat()
        
        db.commit()
        db.refresh(db_question)
        return db_question