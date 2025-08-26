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
    options: List[OptionModel]

class MCQBatchModel(BaseModel):
    questions: List[MCQModel]

class MSQModel(BaseModel):
    question_text: str
    options: List[OptionModel]

class MSQBatchModel(BaseModel):
    questions: List[MSQModel]

class NumericalModel(BaseModel):
    question_text: str
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
            
            prompt = f"""Generate exactly {section.total_questions} high-quality multiple-choice questions (MCQs) for a section named "{section.name}" for exam "{exam_name}".
            
            Requirements:
            - Generate exactly {section.total_questions} questions (this is critical)
            - Each question must have exactly 4 options
            - Only one option should be correct per question
            - Questions should be challenging but fair
            - Each question is worth {section.marks_per_question} marks
            - Do not include explanations (we'll generate those later)
            - Focus on creating {section.total_questions} complete questions
            
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
            
            # Check if we got enough questions
            total_received = len(result.questions)
            logger.info(f"Received {total_received} questions, needed {section.total_questions}")
            
            if total_received < section.total_questions:
                logger.warning(f"Received fewer questions than requested: {total_received} < {section.total_questions}")
            
            # Convert to our schema - take exactly the number we need
            questions = []
            for q in result.questions[:section.total_questions]:  # Take exactly what we need
                mcq = MCQQuestion(
                    question_text=q.question_text,
                    explanation="",  # Empty explanation for now
                    options=[Option(text=opt.text, is_correct=opt.is_correct) for opt in q.options]
                )
                questions.append(mcq)
            
            logger.info(f"Successfully generated {len(questions)} MCQ questions")
            
            # If we still don't have enough questions, raise an error
            if len(questions) < section.total_questions:
                raise ValueError(f"Failed to generate enough questions. Requested: {section.total_questions}, Generated: {len(questions)}")
            
            return questions
        except Exception as e:
            logger.error(f"Error generating MCQ questions: {str(e)}")
            raise
    
    def _generate_msq_questions(self, section: Section) -> List[MSQQuestion]:
        """Generate MSQ (multiple select) questions using Gemini"""
        try:
            # Get exam name from the relationship
            exam_name = section.exam.name if section.exam else "Exam"
            
            prompt = f"""Generate exactly {section.total_questions} high-quality multiple-select questions (MSQs) for a section named "{section.name}" for exam "{exam_name}".
            
            Requirements:
            - Generate exactly {section.total_questions} questions (this is critical)
            - Each question must have exactly 4 options
            - Multiple options can be correct (between 1-3 options can be correct)
            - Questions should be challenging but fair
            - Each question is worth {section.marks_per_question} marks
            - Do not include explanations (we'll generate those later)
            - Focus on creating {section.total_questions} complete questions
            
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
            
            # Check if we got enough questions
            total_received = len(result.questions)
            logger.info(f"Received {total_received} questions, needed {section.total_questions}")
            
            if total_received < section.total_questions:
                logger.warning(f"Received fewer questions than requested: {total_received} < {section.total_questions}")
            
            # Convert to our schema - take exactly the number we need
            questions = []
            for q in result.questions[:section.total_questions]:  # Take exactly what we need
                msq = MSQQuestion(
                    question_text=q.question_text,
                    explanation="",  # Empty explanation for now
                    options=[Option(text=opt.text, is_correct=opt.is_correct) for opt in q.options]
                )
                questions.append(msq)
            
            logger.info(f"Successfully generated {len(questions)} MSQ questions")
            
            # If we still don't have enough questions, raise an error
            if len(questions) < section.total_questions:
                raise ValueError(f"Failed to generate enough questions. Requested: {section.total_questions}, Generated: {len(questions)}")
            
            return questions
        except Exception as e:
            logger.error(f"Error generating MSQ questions: {str(e)}")
            raise
    
    def _generate_numerical_questions(self, section: Section) -> List[NumericalQuestion]:
        """Generate numerical questions using Gemini"""
        try:
            # Get exam name from the relationship
            exam_name = section.exam.name if section.exam else "Exam"
            
            prompt = f"""Generate exactly {section.total_questions} high-quality numerical questions for a section named "{section.name}" for exam "{exam_name}".
            
            Requirements:
            - Generate exactly {section.total_questions} questions (this is critical)
            - Each question should have a precise numerical answer
            - Questions should be challenging but fair
            - Each question is worth {section.marks_per_question} marks
            - Do not include explanations (we'll generate those later)
            - Focus on creating {section.total_questions} complete questions
            
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
            
            # Check if we got enough questions
            total_received = len(result.questions)
            logger.info(f"Received {total_received} questions, needed {section.total_questions}")
            
            if total_received < section.total_questions:
                logger.warning(f"Received fewer questions than requested: {total_received} < {section.total_questions}")
            
            # Convert to our schema - take exactly the number we need
            questions = []
            for q in result.questions[:section.total_questions]:  # Take exactly what we need
                numerical = NumericalQuestion(
                    question_text=q.question_text,
                    explanation="",  # Empty explanation for now
                    answer=q.answer
                )
                questions.append(numerical)
            
            logger.info(f"Successfully generated {len(questions)} numerical questions")
            
            # If we still don't have enough questions, raise an error
            if len(questions) < section.total_questions:
                raise ValueError(f"Failed to generate enough questions. Requested: {section.total_questions}, Generated: {len(questions)}")
            
            return questions
        except Exception as e:
            logger.error(f"Error generating numerical questions: {str(e)}")
            raise
    
    def generate_explanation(self, question_text: str, question_type: str, correct_answer=None, options=None) -> str:
        """Generate explanation for a specific question"""
        try:
            if question_type in ["MCQ", "MSQ"] and options:
                correct_options = [opt for opt in options if opt.get('is_correct', False)]
                correct_texts = [opt['text'] for opt in correct_options]
                
                prompt = f"""Generate a clear and concise explanation for this {question_type} question:
                
                Question: {question_text}
                
                Options: {[opt['text'] for opt in options]}
                Correct Answer(s): {correct_texts}
                
                Please provide a brief explanation of why the correct answer(s) is/are right and why the other options are incorrect.
                Keep it educational and focused."""
                
            elif question_type == "NUM" and correct_answer is not None:
                prompt = f"""Generate a clear and concise explanation for this numerical question:
                
                Question: {question_text}
                Correct Answer: {correct_answer}
                
                Please provide a step-by-step solution showing how to arrive at the correct answer.
                Keep it educational and focused."""
            else:
                return "Explanation not available."
            
            logger.info(f"Generating explanation for {question_type} question")
            
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt
            )
            
            explanation = response.text.strip()
            logger.info("Successfully generated explanation")
            
            return explanation
            
        except Exception as e:
            logger.error(f"Error generating explanation: {str(e)}")
            return "Explanation could not be generated."