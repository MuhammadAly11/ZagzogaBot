import json
import os
import subprocess
from pathlib import Path
from typing import Optional, Tuple, List
import aiofiles
from pydantic import ValidationError

from ..models.quiz import Quiz, UserQuizState

async def parse_quiz_json(file_path: Path) -> Tuple[Optional[Quiz], Optional[str]]:
    """Parse and validate quiz JSON file."""
    try:
        async with aiofiles.open(file_path, 'r') as f:
            content = await f.read()
        quiz_data = json.loads(content)
        
        # Add serial numbers if not present
        if "questions" in quiz_data:
            for i, q in enumerate(quiz_data["questions"], 1):
                if "sn" not in q:
                    q["sn"] = str(i)
        
        try:
            quiz = Quiz.model_validate(quiz_data)
            return quiz, None
        except ValidationError as e:
            # Create a more user-friendly error message
            error_details = []
            for error in e.errors():
                field = " -> ".join(str(loc) for loc in error["loc"])
                msg = error["msg"]
                if "type=missing" in str(error):
                    error_details.append(f"Missing required field: {field}")
                else:
                    error_details.append(f"Invalid {field}: {msg}")
            
            return None, "Quiz format error:\n" + "\n".join(error_details)
            
    except json.JSONDecodeError as e:
        line_no = e.lineno
        col_no = e.colno
        return None, f"Invalid JSON format at line {line_no}, column {col_no}. Please check your file."
    except Exception as e:
        return None, f"Error reading quiz file: {str(e)}"

async def generate_quiz_pdf(quiz: Quiz, user_state: UserQuizState, output_path: Path) -> Tuple[bool, Optional[str]]:
    """Generate PDF version of the quiz with answers using Typst."""
    try:
        # Create a temporary Typst file
        typst_content = generate_typst_content(quiz, user_state)
        temp_typst_file = output_path.with_suffix('.typ')
        
        async with aiofiles.open(temp_typst_file, 'w') as f:
            await f.write(typst_content)
        
        # Run typst compile command
        result = subprocess.run(
            ['typst', 'compile', str(temp_typst_file), str(output_path)],
            capture_output=True,
            text=True
        )
        
        # Clean up temporary file
        temp_typst_file.unlink()
        
        if result.returncode != 0:
            return False, f"Error compiling PDF: {result.stderr}"
            
        return True, None
    except Exception as e:
        return False, f"Error generating PDF: {str(e)}"

def get_question_options(question: 'QuizQuestion') -> List[str]:
    """Get all available options for a question."""
    options = [question.a, question.b, question.c]
    if question.d:
        options.append(question.d)
    if question.e:
        options.append(question.e)
    if question.f:
        options.append(question.f)
    if question.g:
        options.append(question.g)
    return options

def get_correct_option_index(question: 'QuizQuestion') -> int:
    """Get the index (0-based) of the correct answer."""
    return ord(question.answer.lower()) - ord('a')

def generate_typst_content(quiz: Quiz, user_state: UserQuizState) -> str:
    """Generate Typst content for the quiz."""
    # Calculate percentage score
    percentage = (user_state.score / user_state.total_questions) * 100
    
    # Create Typst content
    content = f'''#import "@local/quizst:0.1.0": *

#let quiz_data = (
  type: "{quiz.type}",
  title: "{quiz.title}",
'''
    
    if quiz.type == "lesson":
        content += f'''  module: "{quiz.module or ''}",
  subject: "{quiz.subject or ''}",
  lesson: "{quiz.lesson or ''}",
'''
    else:  # custom mode
        content += f'''  tags: {json.dumps(quiz.tags or [])},
'''
    
    content += f'''  questions: (
'''
    
    # Add each question
    for i, question in enumerate(quiz.questions):
        options = get_question_options(question)
        user_answer = user_state.answers[i] if i < len(user_state.answers) else None
        correct_index = get_correct_option_index(question)
        
        content += f'''    (
      sn: "{question.sn}",
      source: "{question.source or ''}",
      question: "{question.question}",
      options: ({", ".join(f'"{opt}"' for opt in options)}),
      correct: {correct_index + 1},
      selected: {ord(user_answer.lower()) - ord('a') + 1 if user_answer else "none"}
    ),
'''
    
    content += f'''  ),
  score: "{user_state.score}/{user_state.total_questions} ({percentage:.1f}%)"
)

#show: quiz.with(quiz_data)
'''
    return content

def format_quiz_question(question: str, options: List[str], current_num: int, total: int) -> str:
    """Format quiz question for display in Telegram."""
    options_text = "\n".join(f"{chr(ord('a') + i)}. {opt}" for i, opt in enumerate(options))
    return f"Question {current_num + 1}/{total}\n\n{question}\n\n{options_text}" 