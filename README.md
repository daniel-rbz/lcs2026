# lcs2026 Hackathon Starter

Super minimal Flask backend + frontend skeleton.

## Structure

- `backend/app.py`: Flask app and API endpoint
- `backend/requirements.txt`: Python dependencies
- `frontend/index.html`: Basic UI
- `frontend/app.js`: Calls backend API
- `frontend/styles.css`: Basic styles

## Quick start

1. Create and activate a virtual environment.
2. Install dependencies:
   ```bash
   pip install -r backend/requirements.txt
   ```
3. Run the Flask app:
   ```bash
   python backend/app.py
   ```
4. Open http://127.0.0.1:5000 in your browser.

## API endpoint

- `GET /api/health`
