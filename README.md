# Telegram Quiz Bot

An interactive Telegram bot that allows users to take quizzes from JSON files and generates PDF reports using Typst with the Quizst template.

## Features

- Interactive quiz experience through Telegram
- Support for multiple-choice questions
- Immediate feedback on answers
- PDF report generation using Typst
- User-friendly interface with inline keyboards

## Prerequisites

- Python 3.8 or higher
- A Telegram Bot Token (get it from [@BotFather](https://t.me/botfather))
- [Typst](https://typst.app/) installed and available in PATH
- [Quizst Typst Template](https://github.com/MuhammadAly11/Quizst) installed in Typst's template directory
- Quiz JSON files from [ZagazogaWebApp](https://github.com/MuhammadAly11/ZagazogaWebApp)

## Installation

1. Install Typst:
   - Follow the instructions at [typst.app](https://typst.app/) to install Typst
   - Make sure the `typst` command is available in your PATH

2. Install Quizst Template:
   ```bash
   # Create Typst templates directory if it doesn't exist
   mkdir -p ~/.local/share/typst/packages/local/quizst/0.1.0
   
   # Clone Quizst template
   git clone https://github.com/MuhammadAly11/Quizst.git ~/.local/share/typst/packages/local/quizst/0.1.0
   ```

3. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/telegram-quiz-bot.git
   cd telegram-quiz-bot
   ```

4. Create a virtual environment and activate it:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

5. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

6. Create a `.env` file in the project root and add your Telegram Bot Token:
   ```
   TELEGRAM_BOT_TOKEN=your_bot_token_here
   ```

## Usage

1. Start the bot:
   ```bash
   python main.py
   ```

2. In Telegram:
   - Start a chat with your bot
   - Send `/start` to get instructions
   - Follow the instructions to download a quiz JSON file
   - Upload the JSON file to start the quiz
   - Answer questions by clicking the inline keyboard buttons
   - Receive your score and PDF report when finished

## JSON File Format

The quiz JSON file supports two formats from ZagazogaWebApp:

### Lesson Mode
```json
{
  "type": "lesson",
  "title": "Quiz Title",
  "module": "Module Name",
  "subject": "Subject Name",
  "lesson": "Lesson Name",
  "questions": [
    {
      "sn": "1",
      "source": "Optional source reference",
      "question": "Which chamber of the heart receives deoxygenated blood?",
      "answer": "b",
      "a": "Left Atrium",
      "b": "Right Atrium",
      "c": "Left Ventricle",
      "d": "Right Ventricle"
    }
  ]
}
```

### Custom Mode
```json
{
  "type": "custom",
  "title": "Programming Basics",
  "module": "Computer Science",
  "tags": ["programming", "beginners"],
  "questions": [
    {
      "sn": "1",
      "source": "Variables",
      "question": "What is a variable?",
      "answer": "b",
      "a": "A fixed value",
      "b": "A container for data",
      "c": "A function",
      "d": "A language"
    }
  ]
}
```

Note: Each question can have up to 7 options (a through g). Options d through g are optional.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 