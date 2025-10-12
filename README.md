# AI Travel Planner

A small Streamlit app that uses Google's GenAI (Gemini) to generate concise travel plans from user inputs.

What the app provides
- A web form to enter: Destination, Trip Start/End dates (optional), Number of days, Home location, Budget, Trip type, and Interests.
- Generates a short trip summary, day-by-day itinerary, budget breakdown, packing list, and local tips using the Google GenAI SDK.
- A sidebar feedback form where users can submit feedback and pick an emotion label. Feedback is persisted to `feedbacks.txt`.

## Files
- `app.py` - Main Streamlit application.
- `README.md` - This file.
- `.env.example` - Example environment file you can copy to `.env` locally.
- `.env` (not committed) - Optional local file to store `GEMINI_API_KEY` for local testing.
- `feedbacks.txt` - Created at runtime when users submit feedback (contains recent feedback entries).

## Requirements
The project includes `requirements.txt`. Primary dependencies:
- streamlit
- python-dotenv
- google-genai

## Setup & Run

1. Create and activate a Python virtual environment (recommended):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
pip install -r requirements.txt
```

3. Provide an API key for the Google GenAI SDK. Locally you can copy `.env.example` to `.env` and replace the placeholder:

```powershell
copy .env.example .env
# then edit .env and set GEMINI_API_KEY
```

Notes:
- The app calls `load_dotenv('.env')` at startup to load that file into the environment. If you prefer not to use `.env`, export `GEMINI_API_KEY` into your shell or use your platform's secret manager when deploying.
- A `.gitignore` is included that ignores `.env` to help avoid committing secrets. Do NOT commit `.env` to version control.

4. Run the Streamlit app:

```powershell
streamlit run "app.py"
```

5. Open the URL shown by Streamlit in your browser (usually http://localhost:8501).

## Behavior notes

- If both start and end dates are provided, the app computes the trip duration automatically (inclusive). If the end date is before the start date, the app shows an error.
- You can still manually adjust "Number of Days".
- The Home Location field helps the AI suggest realistic logistics (nearest airport, routes, etc.).

## Implementation notes (recent updates)

- Robust budget parsing
- Offline fallback: if the GenAI/API key service fails, the app uses a rule-based offline response generator. 
- Stable randomness: the offline generator uses the `random` module correctly and safely selects interests when provided as a comma-separated string.

These changes improve robustness for users testing without a working GenAI key and reduce crashes from malformed inputs.

## Feedback feature
- The sidebar contains a Feedback section with a short text area. When submitted, feedback entries are saved to `feedbacks.txt` and shown in the sidebar.

## Troubleshooting
- If you see: "google-genai SDK not installed", run:

```powershell
pip install google-genai
```

- If you get model errors (e.g., model not found or permission denied), try:
  - Use model `gemini-2.5-flash` in the code or check the model name your API key is allowed to access.
  - Verify `GEMINI_API_KEY` is valid and has GenAI permissions.

- If you see errors about budget parsing or `int()` conversions, ensure your budget input is a number or in a format like `50000`, `50,000`, `50000 INR`, or `$800`. The app will try to parse common formats but malformed inputs may still cause issues in older versions.
- If you see "AI service failed — using rule-based offline plan", the fallback will be used automatically and a friendly message is shown in the UI. The offline plan should display and be downloadable as text.

## Security & deployment

Deployment: https://arun-sajwan-ai-travel-planner-app-7vwfoi.streamlit.app/


