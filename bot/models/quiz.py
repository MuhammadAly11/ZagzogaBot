from typing import List, Optional, Literal, Dict
from pydantic import BaseModel, Field, model_validator

class QuizQuestion(BaseModel):
    sn: str
    source: Optional[str] = None
    question: str
    answer: str  # a, b, c, d, etc.
    a: str
    b: str
    c: str
    d: Optional[str] = None
    e: Optional[str] = None
    f: Optional[str] = None
    g: Optional[str] = None

class Quiz(BaseModel):
    type: Literal["lesson", "custom"] = "custom"
    title: Optional[str] = None
    module: Optional[str] = None
    subject: Optional[str] = None  # For lesson mode
    lesson: Optional[str] = None   # For lesson mode
    tags: Optional[List[str]] = None  # For custom mode
    questions: List[QuizQuestion]

    @model_validator(mode='before')
    @classmethod
    def set_defaults(cls, data: dict) -> dict:
        """Set default values and handle missing fields."""
        if isinstance(data, dict):
            # If title is missing, construct it from module/subject/lesson
            if 'title' not in data or not data.get('title'):
                if data.get('type') == 'lesson':
                    parts = []
                    if data.get('module'): parts.append(data['module'])
                    if data.get('subject'): parts.append(data['subject'])
                    if data.get('lesson'): parts.append(data['lesson'])
                    data['title'] = ' - '.join(parts) if parts else 'Untitled Quiz'
                else:
                    data['title'] = data.get('module', 'Untitled Quiz')
            
            # Ensure type is set
            if 'type' not in data:
                data['type'] = 'custom'
        return data
    
class UserQuizState(BaseModel):
    current_question: int = 0
    score: int = 0
    total_questions: int = 0
    answers: List[str] = Field(default_factory=list)  # List of answers (a, b, c, d, etc.)
    quiz: Quiz  # Make quiz required