import os
import uuid
from fastapi import UploadFile, HTTPException, status
from sqlalchemy.orm import Session
import google.generativeai as genai

from app.repositories.exam_repository import ExamRepository
from app.core.config import get_gemini_api_key

class SectionService:
    def __init__(self):
        self.exam_repository = ExamRepository()
        get_gemini_api_key()

    async def upload_syllabus(self, db: Session, section_id: int, file: UploadFile):
        # 1. Check if section exists
        section = self.exam_repository.get_section(db, section_id)
        if not section:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Section with ID {section_id} not found")

        # 2. Validate file type
        if file.content_type != "application/pdf":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only PDF files are allowed")

        # 3. Save the uploaded file to a temporary location
        temp_dir = "temp_files"
        os.makedirs(temp_dir, exist_ok=True)

        # Generate a unique filename to avoid collisions
        temp_filename = f"{uuid.uuid4()}.pdf"
        temp_filepath = os.path.join(temp_dir, temp_filename)

        try:
            with open(temp_filepath, "wb") as buffer:
                buffer.write(await file.read())

            # 4. Upload file to Gemini File API
            syllabus_file = genai.upload_file(
                path=temp_filepath,
                display_name=file.filename
            )

            # 5. Update the section in the database
            updated_section = self.exam_repository.update_section_syllabus(db, section_id, syllabus_file.uri)

            return {"file_uri": updated_section.syllabus_file_uri}

        except Exception as e:
            # Log the error for debugging
            print(f"Error uploading syllabus for section {section_id}: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to upload syllabus")

        finally:
            # 6. Clean up the temporary file
            if os.path.exists(temp_filepath):
                os.remove(temp_filepath)
