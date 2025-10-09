# AI Travel Planner

A simple Streamlit app that uses Google's GenAI (Gemini) to generate concise travel plans based on user inputs.

This project provides a web form where users can enter:

- Destination
- Trip Start Date and Trip End Date (used to compute trip duration)
- Number of Days (will be computed from dates if provided)
- Home Location / Starting Point
- Budget
- Type of Trip (Adventure, Family, Solo, etc.)
- Interests (free-text)

The app sends a structured prompt to the Google GenAI SDK and returns a short trip summary, day-by-day itinerary, budget breakdown, packing list, and local tips.

## Files

- `app1.py` - Main Streamlit application.
- `README.md` - This file.
- `.env` (optional) - Place your `GEMINI_API_KEY` or `GOOGLE_API_KEY` here.

## Requirements
 `requirements.txt` is included.
  Primary dependencies:

- streamlit
- python-dotenv
- google-genai

## Setup & Run

1. Create a Python virtual environment (recommended):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
pip install -r requirements.txt
```

3. (Optional) Create a `.env` file in the project root with your API key:

```text
GEMINI_API_KEY=your_api_key_here
# or
GOOGLE_API_KEY=your_api_key_here
```

4. Run the Streamlit app:

```powershell
streamlit run "app1.py"
```

5. Open the URL shown by Streamlit in your browser (usually http://localhost:8502).

## Notes & Behavior

- If you supply both start and end dates, the app computes the trip duration automatically and uses it for the plan. If end date is before start date, the app will show an error.
- You can still manually adjust "Number of Days" if you prefer.
- The "Home Location" field helps the AI suggest realistic travel logistics (for example, nearest airport, suggested departure time, or route planning).

## Troubleshooting

- If you see the error "google-genai SDK not installed", run:

```powershell
pip install google-genai
```

- If you get model errors (e.g., model not found), try using the default model `gemini-2.5-flash` or check your API key permissions.

## License

This repository is provided as-is for educational/demo purposes.