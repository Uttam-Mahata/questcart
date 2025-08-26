from google import genai
from google.genai import types
from typing import List, Dict, Any, Union, Optional
import os
import json
import logging
from dotenv import load_dotenv
from pydantic import BaseModel, Field

from app.models.models import Section, QuestionType
from app.schemas.schemas import QuestionUnion, MCQQuestion, MSQQuestion, NumericalQuestion, Option

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

# Initialize the Gemini client
api_key = os.getenv("GEMINI_API_KEY", "your-api-key")
logger.info(f"Initializing Gemini client with API key {'provided' if api_key != 'your-api-key' else 'NOT PROVIDED'}")
client = genai.Client(api_key=api_key)

# Define Pydantic models for schema validation
class OptionModel(BaseModel):
    text: str
    is_correct: bool

class MCQModel(BaseModel):
    question_text: str
    explanation: str
    options: List[OptionModel]

class MCQBatchModel(BaseModel):
    questions: List[MCQModel]

class MSQModel(BaseModel):
    question_text: str
    explanation: str
    options: List[OptionModel]

class MSQBatchModel(BaseModel):
    questions: List[MSQModel]

class NumericalModel(BaseModel):
    question_text: str
    explanation: str
    answer: float

class NumericalBatchModel(BaseModel):
    questions: List[NumericalModel]

class GeminiService:
    def __init__(self):
        self.client = client
        self.model = "gemini-2.0-flash"  # Using Gemini 2.0 Flash model
    
    def generate_questions(self, section: Section) -> List[QuestionUnion]:
        """Generate questions using Gemini API based on section requirements"""
        try:
            # Generate questions based on section type
            question_type = section.question_type
            
            logger.info(f"Generating {section.total_questions} questions of type {question_type} for section {section.name}")
            
            if question_type == QuestionType.MCQ:
                return self._generate_mcq_questions(section)
            elif question_type == QuestionType.MSQ:
                return self._generate_msq_questions(section)
            elif question_type == QuestionType.NUM:
                return self._generate_numerical_questions(section)
            else:
                raise ValueError(f"Unsupported question type: {question_type}")
        except Exception as e:
            logger.error(f"Error generating questions: {str(e)}")
            raise
    
    def _generate_mcq_questions(self, section: Section) -> List[MCQQuestion]:
        """Generate MCQ questions using Gemini"""
        try:
            # Get exam name from the relationship
            exam_name = section.exam.name if section.exam else "Exam"
            
            prompt = f"""Generate {section.total_questions} high-quality multiple-choice questions (MCQs) for a section named "{section.name}" for exam "{exam_name}".
            
            Requirements:
            - Each question must have exactly 4 options
            - Only one option should be correct
            - Questions should be challenging but fair
            - Each question is worth {section.marks_per_question} marks
            - If applicable, negative marking is {section.negative_marks} marks
            
            Please provide your response in a structured JSON format without any extra text or explanations.
            """
            
            logger.info(f"Sending MCQ prompt to Gemini: {prompt[:100]}...")
            
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config={
                    'response_mime_type': 'application/json',
                    'response_schema': MCQBatchModel,
                },
            )
            
            logger.info("Received response from Gemini")
            
            # Log the raw response for debugging
            logger.info(f"Raw response: {response.text}")
            
            result = response.parsed
            
            # Convert to our schema
            questions = []
            for q in result.questions[:section.total_questions]:  # Ensure we only take the needed number
                mcq = MCQQuestion(
                    question_text=q.question_text,
                    explanation=q.explanation,
                    options=[Option(text=opt.text, is_correct=opt.is_correct) for opt in q.options]
                )
                questions.append(mcq)
            
            logger.info(f"Successfully generated {len(questions)} MCQ questions")
            return questions
        except Exception as e:
            logger.error(f"Error generating MCQ questions: {str(e)}")
            raise
    
    def _generate_msq_questions(self, section: Section) -> List[MSQQuestion]:
        """Generate MSQ (multiple select) questions using Gemini"""
        try:
            # Get exam name from the relationship
            exam_name = section.exam.name if section.exam else "Exam"
            
            prompt = f"""Generate {section.total_questions} high-quality multiple-select questions (MSQs) for a section named "{section.name}" for exam "{exam_name}".
            
            Requirements:
            - Each question must have exactly 4 options
            - Multiple options can be correct (between 1-3 options can be correct)
            - Questions should be challenging but fair
            - Each question is worth {section.marks_per_question} marks
            - If applicable, negative marking is {section.negative_marks} marks
            
            Please provide your response in a structured JSON format without any extra text or explanations.
            """
            
            logger.info(f"Sending MSQ prompt to Gemini: {prompt[:100]}...")
            
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config={
                    'response_mime_type': 'application/json',
                    'response_schema': MSQBatchModel,
                },
            )
            
            logger.info("Received response from Gemini")
            
            # Log the raw response for debugging
            logger.info(f"Raw response: {response.text}")
            
            result = response.parsed
            
            # Convert to our schema
            questions = []
            for q in result.questions[:section.total_questions]:  # Ensure we only take the needed number
                msq = MSQQuestion(
                    question_text=q.question_text,
                    explanation=q.explanation,
                    options=[Option(text=opt.text, is_correct=opt.is_correct) for opt in q.options]
                )
                questions.append(msq)
            
            logger.info(f"Successfully generated {len(questions)} MSQ questions")
            return questions
        except Exception as e:
            logger.error(f"Error generating MSQ questions: {str(e)}")
            raise
    
    def _generate_numerical_questions(self, section: Section) -> List[NumericalQuestion]:
        """Generate numerical questions using Gemini"""
        try:
            # Get exam name from the relationship
            exam_name = section.exam.name if section.exam else "Exam"
            
            prompt = f"""Generate {section.total_questions} high-quality numerical questions for a section named "{section.name}" for exam "{exam_name}".
            
            Requirements:
            - Each question should have a precise numerical answer
            - Questions should be challenging but fair
            - Each question is worth {section.marks_per_question} marks
            - If applicable, negative marking is {section.negative_marks} marks
            
            Please provide your response in a structured JSON format without any extra text or explanations.
            """
            
            logger.info(f"Sending numerical prompt to Gemini: {prompt[:100]}...")
            
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config={
                    'response_mime_type': 'application/json',
                    'response_schema': NumericalBatchModel,
                },
            )
            
            logger.info("Received response from Gemini")
            
            # Log the raw response for debugging
            logger.info(f"Raw response: {response.text}")
            
            result = response.parsed
            
            # Convert to our schema
            questions = []
            for q in result.questions[:section.total_questions]:  # Ensure we only take the needed number
                numerical = NumericalQuestion(
                    question_text=q.question_text,
                    explanation=q.explanation,
                    answer=q.answer
                )
                questions.append(numerical)
            
            logger.info(f"Successfully generated {len(questions)} numerical questions")
            return questions
        except Exception as e:
            logger.error(f"Error generating numerical questions: {str(e)}")
            raise