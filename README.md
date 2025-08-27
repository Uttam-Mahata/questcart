# Automated Question Paper Creation Application

An AI-powered application that generates custom question papers using the Gemini API. This application allows you to create exams with multiple sections and automatically generates questions for each section based on the requirements.

## Features

- Create exams with configurable sections
- Section configurations include:
  - Section name
  - Number of total questions
  - Number of questions to attempt
  - Marks per question
  - Negative marking settings
  - Question types (MCQ, MSQ, Numerical)
- AI-powered question generation using Google's Gemini API
- Generate questions section by section
- Persistent storage in SQLite database
- RESTful API for frontend integration

## Technology Stack

- FastAPI - High-performance web framework
- SQLAlchemy - SQL toolkit and ORM
- Google Gemini API - AI-powered content generation
- Pydantic - Data validation
- SQLite - Database (can be configured to use other databases)

## Setup Instructions

### Prerequisites

- Python 3.8+
- Gemini API key (from Google AI Studio)

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/qpgen.git
   cd qpgen
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Create a .env file:
   ```
   cp .env.example .env
   ```

4. Edit the .env file and add your Gemini API key:
   ```
   GEMINI_API_KEY=your_api_key_here
   ```

### Running the Application

Start the FastAPI server:

```
python main.py
```

The API will be available at http://localhost:8000.

- API documentation: http://localhost:8000/docs
- Interactive API explorer: http://localhost:8000/redoc

## API Usage

### Creating an Exam

```
POST /api/exams/
```

Request body:
```json
{
  "name": "Physics Mid-term",
  "time_minutes": 180,
  "sections": [
    {
      "name": "Mechanics",
      "total_questions": 10,
      "questions_to_attempt": 8,
      "marks_per_question": 5.0,
      "negative_marking_allowed": true,
      "negative_marks": 1.0,
      "question_type": "MCQ"
    },
    {
      "name": "Thermodynamics",
      "total_questions": 5,
      "questions_to_attempt": 5,
      "marks_per_question": 10.0,
      "negative_marking_allowed": false,
      "question_type": "NUM"
    }
  ]
}
```

### Getting Exam Details

```
GET /api/exams/{exam_id}
```

### Generating Questions for a Section

```
POST /api/exams/sections/{section_id}/generate-questions
```

### Getting Questions for a Section

```
GET /api/exams/sections/{section_id}/questions
```

## Using Gemini API Features

The application uses two key features of the Gemini API:

1. **Structured Response** - Ensures questions are generated in a consistent format suitable for different question types (MCQ, MSQ, Numerical).

2. **Function Calling** - Enables advanced question generation with specific formatting requirements.

## License

MIT
