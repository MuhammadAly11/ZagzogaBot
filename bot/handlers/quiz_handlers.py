import tempfile
from pathlib import Path
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, PollAnswer
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton
import asyncio
import logging
from collections import defaultdict

from ..models.quiz import Quiz, UserQuizState
from ..utils.quiz_utils import parse_quiz_json, generate_quiz_pdf, format_quiz_question, get_question_options

# Configure logging
logging.basicConfig(level=logging.INFO)
router = Router()
logger = logging.getLogger(__name__)

# Dictionary to store active polls and their states
active_polls = {}  # Maps poll_id -> chat_id
user_states = {}   # Maps chat_id -> UserQuizState

@router.message(Command("start"))
async def cmd_start(message: Message):
    """Handle the /start command."""
    kb = InlineKeyboardBuilder()
    kb.button(
        text="🌐 Create Quiz",
        url="https://muhammadaly11.github.io/ZagazogaWebApp/"
    )
    
    welcome_text = (
        "👋 Welcome to the Quiz Bot!\n\n"
        "To start a quiz, you'll need to:\n"
        "1. Click the button below to open ZagazogaWebApp\n"
        "2. Create your quiz and export it as JSON\n"
        "3. Send the JSON file back to me\n\n"
        "Once you send the file, I'll guide you through the quiz using anonymous polls!"
    )
    await message.answer(welcome_text, reply_markup=kb.as_markup())

@router.message(F.document)
async def handle_quiz_file(message: Message, state: FSMContext):
    """Handle uploaded JSON quiz file."""
    if not message.document.file_name.endswith('.json'):
        await message.answer("Please send a JSON file.")
        return

    # Download and parse the file
    with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as temp_file:
        file_path = Path(temp_file.name)
        await message.bot.download(message.document, destination=file_path)
        
    quiz, error = await parse_quiz_json(file_path)
    file_path.unlink()  # Clean up temp file
    
    if error:
        await message.answer(f"Error: {error}")
        return

    # Initialize quiz state
    user_state = UserQuizState(
        quiz=quiz,
        total_questions=len(quiz.questions)
    )
    
    # Store state both in FSM and our local dictionary
    await state.set_data(user_state.model_dump())
    user_states[message.chat.id] = user_state
    logger.info(f"Initialized quiz state for user {message.chat.id}")

    await message.answer(
        f"Starting quiz: {quiz.title or 'Untitled Quiz'}\n"
        f"Total questions: {len(quiz.questions)}\n\n"
        "I'll send all questions as anonymous polls. Answer them in any order!"
    )

    # Send all questions at once
    for i, question in enumerate(quiz.questions):
        options = get_question_options(question)
        correct_option_id = ord(question.answer.lower()) - ord('a')
        
        logger.info(f"Sending question {i + 1} to user {message.chat.id}")
        
        # Send as a quiz poll
        poll = await message.bot.send_poll(
            chat_id=message.chat.id,
            question=f"Question {i + 1}/{len(quiz.questions)}\n\n{question.question}",
            options=options,
            type="quiz",
            correct_option_id=correct_option_id,
            is_anonymous=True,
            protect_content=False
        )
        
        # Store the poll id with the user's chat id
        active_polls[poll.poll.id] = message.chat.id
        logger.info(f"Sent poll {poll.poll.id} to user {message.chat.id} (Question {i + 1})")
        
        # Add a small delay between sending polls to maintain order
        await asyncio.sleep(0.5)

    # Send a message to indicate all questions have been sent
    await message.answer(
        "✅ All questions have been sent!\n"
        "You can answer them in any order.\n"
        "Your final score will be shown once you answer all questions."
    )

@router.poll_answer(F.poll_answer)
async def handle_poll_answer(poll_answer: PollAnswer, state: FSMContext):
    """Handle poll answers."""
    chat_id = None
    try:
        logger.info(f"Received answer for poll {poll_answer.poll_id} from user {poll_answer.user.id}")
        
        # Get chat_id from active_polls
        chat_id = active_polls.get(poll_answer.poll_id)
        if not chat_id:
            logger.warning(f"Received answer for unknown poll {poll_answer.poll_id}")
            return

        # Get user state
        user_state = user_states.get(chat_id)
        if not user_state:
            logger.warning(f"No state found for user {chat_id}")
            # Try to recover state from FSM
            state_data = await state.get_data()
            if state_data:
                try:
                    user_state = UserQuizState.model_validate(state_data)
                    user_states[chat_id] = user_state
                    logger.info(f"Recovered state for user {chat_id}")
                except Exception as e:
                    logger.error(f"Failed to validate state data: {e}")
                    await poll_answer.bot.send_message(
                        chat_id,
                        "Sorry, there was an error with your quiz state. Please start a new quiz with /start"
                    )
                    return
            else:
                await poll_answer.bot.send_message(
                    chat_id,
                    "Sorry, I couldn't find your quiz state. Please start a new quiz with /start"
                )
                return

        # Find which question this poll belongs to
        poll_index = None
        for i, question in enumerate(user_state.quiz.questions):
            if poll_answer.poll_id in active_polls:
                poll_index = i
                break

        if poll_index is None:
            logger.warning(f"Could not find question for poll {poll_answer.poll_id}")
            return

        # Record answer and update score
        selected_option = poll_answer.option_ids[0]  # Get the selected option index
        selected_answer = chr(ord('a') + selected_option)  # Convert to letter (a, b, c, etc.)
        
        # Extend answers list if needed
        while len(user_state.answers) <= poll_index:
            user_state.answers.append(None)
        
        # Update the answer at the correct index
        user_state.answers[poll_index] = selected_answer
        
        # Update score
        if selected_answer.lower() == user_state.quiz.questions[poll_index].answer.lower():
            if user_state.answers[poll_index] is None:  # Only increment score if this is a new answer
                user_state.score += 1
            logger.info(f"Correct answer from user {chat_id} for question {poll_index + 1}")
        else:
            logger.info(f"Incorrect answer from user {chat_id} for question {poll_index + 1}")
        
        # Update state in both places
        try:
            await state.set_data(user_state.model_dump())
            user_states[chat_id] = user_state
            logger.info(f"Successfully updated state for user {chat_id}")
        except Exception as e:
            logger.error(f"Failed to update state: {e}")
            await poll_answer.bot.send_message(
                chat_id,
                "Sorry, there was an error saving your progress. Please start a new quiz with /start"
            )
            return
        
        # Check if all questions are answered
        if all(answer is not None for answer in user_state.answers):
            logger.info(f"Quiz completed for user {chat_id}")
            await finish_quiz(chat_id, user_state, poll_answer.bot)
            # Clean up user state after quiz is complete
            del user_states[chat_id]
            await state.clear()
            # Clean up all active polls for this user
            active_polls_to_remove = [poll_id for poll_id, user_chat_id in active_polls.items() if user_chat_id == chat_id]
            for poll_id in active_polls_to_remove:
                del active_polls[poll_id]
            
    except Exception as e:
        logger.error(f"Error handling poll answer: {e}", exc_info=True)
        # Try to send error message to user
        try:
            if chat_id:
                await poll_answer.bot.send_message(
                    chat_id,
                    "Sorry, there was an error processing your answer. Please try again or restart the quiz with /start"
                )
        except Exception as inner_e:
            logger.error(f"Failed to send error message to user: {inner_e}")

async def finish_quiz(chat_id: int, user_state: UserQuizState, bot):
    """Handle quiz completion and generate PDF."""
    score_text = (
        f"🎉 Quiz completed!\n"
        f"Your score: {user_state.score}/{user_state.total_questions}\n"
        f"({(user_state.score/user_state.total_questions)*100:.1f}%)\n\n"
        f"Generating your PDF report..."
    )
    await bot.send_message(chat_id, score_text)
    
    # Generate and send PDF
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
        pdf_path = Path(temp_file.name)
        
    success, error = await generate_quiz_pdf(user_state.quiz, user_state, pdf_path)
    
    if success:
        await bot.send_document(
            chat_id,
            document=pdf_path,
            caption="Here's your quiz report! 📄"
        )
    else:
        await bot.send_message(chat_id, f"Sorry, couldn't generate PDF: {error}")
    
    pdf_path.unlink()  # Clean up temp file