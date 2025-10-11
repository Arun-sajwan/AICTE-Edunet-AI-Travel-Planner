#!/usr/bin/env python3
"""
AI Travel Planner (Streamlit + Google GenAI / Gemini)

"""
import os
from dotenv import load_dotenv
import streamlit as st

# modern Google GenAI SDK
try:
    from google import genai
except Exception:
    genai = None

load_dotenv(".env")  #  environment variables from .env if present

# If GEMINI_API_KEY is set it will be used; otherwise client may pick env vars.
API_KEY = os.getenv("GEMINI_API_KEY")

def get_client():
    if genai is None:
        raise RuntimeError(
            "Google GenAI SDK not installed. Run: pip install google-genai"
        )
    # Pass api_key explicitly if available
    if API_KEY:
        return genai.Client(api_key=API_KEY)
    else:
        #  pick up GEMINI_API_KEY from environment automatically
        return genai.Client()

def generate_ai_plan(client, destination, days, budget, trip_type, interests, start_date=None, end_date=None, home_location=None, model="gemini-2.5-flash"):
    if client is None:
        raise RuntimeError("GenAI client not configured.")
    # Build a date summary if dates provided
    date_summary = ""
    if start_date and end_date:
        date_summary = f"Trip Dates: {start_date} to {end_date}\n"
    home_summary = ""
    if home_location:
        home_summary = f"Starting From: {home_location}\n"

    prompt = f"""
You are an expert travel planner.
Create a concise and practical travel plan for a student based on these details:

Home Location: {home_location}
Destination: {destination}
Duration: {days} days
Budget: {budget}
Type of Trip: {trip_type}
Interests: {interests}
{date_summary}
{home_summary}

Please include:
1. A short trip summary (2–3 lines)
2. A day-by-day itinerary (activities, landmarks, or attractions)
3. A budget breakdown (approximate in INR or USD)
4. A suggested packing list
5. 2-3 local travel tips or safety advice

Keep it friendly and summarized and use emojis to enhance the text.
"""
    # Call the modern client API
    response = client.models.generate_content(model=model, contents=prompt)
    # response.text is the standard quickstart property
    return getattr(response, "text", str(response))

def main():
    st.set_page_config(page_title="AI Travel Planner", page_icon="🌍")
    st.title("🌍 AI Travel Planner")

    # --- Feedback: load previous feedbacks into session state ---
    if "feedbacks" not in st.session_state:
        st.session_state["feedbacks"] = []
        try:
            if os.path.exists("feedbacks.txt"):
                with open("feedbacks.txt", "r", encoding="utf-8") as f:
                    content = f.read().strip()
                    if content:
                        entries = content.split("\n---\n")
                        st.session_state["feedbacks"] = [e.strip() for e in entries if e.strip()]
        except Exception:
            # If reading fails, keep feedbacks as empty list
            st.session_state["feedbacks"] = []

    # --- Sidebar feedback UI ---
    with st.sidebar:
        st.header("Feedback")
        # Emotion selector (emoji) for quick sentiment
        emotion_options = [
            ("😍", "Very Happy"),
            ("😊", "Happy"),
            ("😐", "Neutral"),
            ("😕", "Unsatisfied"),
            ("😡", "Angry"),
        ]
        # Display emoji labels horizontally using columns
        cols = st.columns(len(emotion_options))
        selected_emoji = st.session_state.get("feedback_emotion", "😊")
        for idx, (emoji, label) in enumerate(emotion_options):
            if cols[idx].button(f"{emoji}\n{label}", key=f"emo_{idx}"):
                selected_emoji = emoji
                st.session_state["feedback_emotion"] = emoji

        # Also allow a compact selectbox as fallback
        selected_emoji = st.selectbox("Or pick one:", [e for e, _ in emotion_options], index=[e for e, _ in emotion_options].index(selected_emoji) if selected_emoji in [e for e, _ in emotion_options] else 1, key="feedback_emotion_select")

        feedback_text = st.text_area("Share your feedback or suggestions:", key="feedback_text", height=140)
        if st.button("Submit Feedback", key="submit_feedback"):
            if feedback_text and feedback_text.strip():
                emoji_to_save = st.session_state.get("feedback_emotion", selected_emoji)
                entry = f"{emoji_to_save} {feedback_text.strip()}"
                # save to session state
                st.session_state.setdefault("feedbacks", []).append(entry)
                # append to file for persistence
                try:
                    with open("feedbacks.txt", "a", encoding="utf-8") as f:
                        f.write(entry + "\n---\n")
                    st.success("Thanks! Your feedback has been submitted.")
                    # clear the text area and reset emotion
                    st.session_state["feedback_text"] = ""
                    st.session_state["feedback_emotion"] = "😊"
                except Exception as e:
                    st.error(f"Could not save feedback: {e}")
            else:
                st.warning("Please enter some feedback before submitting.")

        # Optionally show a small summary of collected feedbacks
        if st.session_state.get("feedbacks"):
            st.markdown(f"**Feedback count:** {len(st.session_state['feedbacks'])}")
            with st.expander("View recent feedbacks"):
                for i, fb in enumerate(reversed(st.session_state.get("feedbacks", [])[-10:]), 1):
                    st.write(f"{i}. {fb}")
        st.success("Thank you for using the AI Travel Planner!")
    if genai is None:
        st.error("google-genai SDK not installed. Run `pip install google-genai` in your environment.")
        st.stop()

    with st.form("trip_form"):
        home_location = st.text_input("Home Location (Starting Point)", placeholder="e.g., My City or Home Address")
        destination = st.text_input("Destination", placeholder="e.g., Paris, Goa, Tokyo")
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Trip Start Date")
        with col2:
            end_date = st.date_input("Trip End Date")

        # Compute duration from dates (inclusive) and use as default for days input
        auto_days = None
        if start_date and end_date:
            delta = end_date - start_date
            if delta.days >= 0:
                auto_days = delta.days + 1

        days_default = auto_days if auto_days is not None else 5
        days = st.number_input("Number of Days", min_value=1, max_value=365, value=days_default)
        if auto_days is not None:
            st.caption(f"Duration computed from dates: {auto_days} day(s) (inclusive)")
        budget = st.text_input("Total Budget", placeholder="e.g., 50000 INR or $800")
        trip_type = st.selectbox(
            "Type of Trip",
            ["Adventure", "Family", "Solo", "Honeymoon", "Business", "Cultural", "Relaxation"],
        )
        interests = st.text_area("Your Interests", placeholder="e.g., beaches, food, nightlife, shopping")
        st.info("Please ensure that the API key(.eve file) has the necessary permissions to access the specified model.")
        submitted = st.form_submit_button("✨ Generate My Travel Plan")

    if submitted:
        if not destination.strip():
            st.warning("Please enter a destination.")
            return
        if not home_location.strip():
            st.warning("Please enter your home location.")
            return

        # Validate dates (end must not be before start)
        if start_date and end_date and end_date < start_date:
            st.error("Trip End Date must be the same or after Trip Start Date.")
            return
        if not budget.strip():
            st.warning("Please enter your budget.")
            return
        try:
            client = get_client()
        except Exception as e:
            st.error(f"Could not create GenAI client: {e}")
            return

        with st.spinner("Generating your AI travel plan..."):
            try:
                plan = generate_ai_plan(
                    client,
                    destination,
                    days,
                    budget,
                    trip_type,
                    interests,
                    start_date=start_date,
                    end_date=end_date,
                    home_location=home_location,
                )
                st.subheader("🧳 Your AI Travel Planner")
                st.write(plan)

                st.download_button(
                    "💾 Download Plan as Text",
                    data=plan,
                    file_name=f"AI_Travel_Planner_{destination.replace(' ', '_')}.txt",
                    mime="text/plain",
                )
            except Exception as e:
                st.error(f"Error generating plan: {e}")
                # Helpful hint for common model-not-found errors:
                st.info("If you see 'model not found (404)', try using model='gemini-2.5-flash' or check your API key permissions.")
                return
            st.balloons()

if __name__ == "__main__":
    main()
