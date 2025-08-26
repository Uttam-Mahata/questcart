import json
from typing import Any, Dict, List, Union
from fastapi import HTTPException, status

def parse_json(json_str: str) -> Any:
    """Parse JSON string safely"""
    try:
        return json.loads(json_str) if json_str else None
    except json.JSONDecodeError:
        return None

def json_serialize(obj: Any) -> str:
    """Convert object to JSON string"""
    try:
        return json.dumps(obj)
    except (TypeError, ValueError):
        return "{}"

def handle_error(message: str, status_code: int = status.HTTP_400_BAD_REQUEST):
    """Raise HTTPException with error message"""
    raise HTTPException(
        status_code=status_code,
        detail=message
    )

def validate_section_questions(section, questions: List[Any]) -> None:
    """Validate that the correct number of questions are generated"""
    if len(questions) != section.total_questions:
        handle_error(
            f"Expected {section.total_questions} questions, but got {len(questions)}",
            status.HTTP_500_INTERNAL_SERVER_ERROR
        )