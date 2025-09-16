from sqlalchemy.orm import Session
import json
from datetime import datetime
from app.models.models import Exam, Section, Question, QuestionType
from app.schemas.schemas import ExamCreate, SectionCreate


class ExamRepository:
    def create_exam(self, db: Session, exam: ExamCreate) -> Exam:
        # Calculate total marks
        total_marks = 0
        for section in exam.sections:
            total_marks += section.total_questions * section.marks_per_question

        # Create exam record
        db_exam = Exam(
            name=exam.name,
            total_marks=total_marks,
            time_minutes=exam.time_minutes,
            created_at=datetime.now().isoformat()
        )
        db.add(db_exam)
        db.flush()  # Flush to get the exam ID

        # Create section records
        for section_data in exam.sections:
            db_section = Section(
                exam_id=db_exam.id,
                name=section_data.name,
                total_questions=section_data.total_questions,
                questions_to_attempt=section_data.questions_to_attempt,
                marks_per_question=section_data.marks_per_question,
                negative_marking_allowed=section_data.negative_marking_allowed,
                negative_marks=section_data.negative_marks,
                question_type=QuestionType(section_data.question_type.value)
            )
            db.add(db_section)

        db.commit()
        db.refresh(db_exam)
        return db_exam

    def get_exam(self, db: Session, exam_id: int) -> Exam:
        return db.query(Exam).filter(Exam.id == exam_id).first()

    def get_all_exams(self, db: Session, skip: int = 0, limit: int = 100):
        return db.query(Exam).offset(skip).limit(limit).all()

    def get_section(self, db: Session, section_id: int) -> Section:
        return db.query(Section).filter(Section.id == section_id).first()

    def get_sections_by_exam(self, db: Session, exam_id: int):
        return db.query(Section).filter(Section.exam_id == exam_id).all()

    def update_section_syllabus(self, db: Session, section_id: int, file_uri: str) -> Section:
        section = self.get_section(db, section_id)
        if not section:
            return None
        section.syllabus_file_uri = file_uri
        db.commit()
        db.refresh(section)
        return section