# Budget Hawk (Laurier Financial OS)

An AI-powered, single-page web dashboard designed to calculate, project, and visually graph a Laurier student's financial runway across their degree.

## Features
- **Dynamic Timeline**: Toggle between Academic Year and Academic Term.
- **Data-Driven**: Pulls real Laurier residence, meal plan, and tuition data.
- **Gemini Copilot**: Upload PDFs/Receipts to auto-extract financial data as custom expenses.
- **Flight Plan Export**: Generate beautiful A4 Financial Statements in PDF format natively!

## Installation Setup (For the Team)

1. Clone the repository.
2. Initialize and activate a Python virtual environment:
   ```bash
   python -m venv env
   .\env\Scripts\activate
   ```
3. Install the specific build dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## API Configuration

1. You will see a `.env.example` file in the root directory.
2. Copy it and rename it to exactly `.env` (this is ignored by Git, so it is safe securely locally).
3. Paste a live Gemini 2.5 Flash API key into it:
   ```text
   GEMINI_API_KEY=your_key_here
   ```

## Running the Dashboard

Simply execute the main application:
```bash
python app.py
```
Then navigate to `http://127.0.0.1:8000` in your browser!
