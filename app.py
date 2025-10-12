#!/usr/bin/env python3
"""
AI Travel Planner (Streamlit + Google GenAI / Gemini)

"""
import os
import random
import re
from dotenv import load_dotenv
import streamlit as st

# modern Google GenAI SDK -------------------------------------------------------------------------------------
try:
    from google import genai
except Exception:
    genai = None

load_dotenv(".env")  #  environment variables from .env if present----------------------------------------------

#  GEMINI_API_KEY is set in env vars.
API_KEY = os.getenv("GEMINI_API_KEY")

def get_client():
    if genai is None:
        raise RuntimeError(
            "Google GenAI SDK not installed. Run: pip install google-genai"
        )
    # Pass api_key explicitly if available:-------------------------------------------------------------------
    if API_KEY:
        return genai.Client(api_key=API_KEY)
    else:
        #  pick up GEMINI_API_KEY from environment automatically:-----------------------------------------------
        return genai.Client()
    
# Prompt passing to AI modal and formate of output generation:---------------------------------------------------------------------------------------------------------------

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
    try:
        response = client.models.generate_content(model=model, contents=prompt)
        # response.text is the standard quickstart property - it may be None
        text = getattr(response, "text", None)
        if not text:
            # fallback to string representation if text is missing
            text = str(response)
        return text

    except Exception as e:
        # ====== FALLBACK RULE-BASED LOGIC ======
        st.warning("⚠️ AI service failed — using rule-based offline plan.")
        offline_response = offline_ai_style_response(home_location, destination, days, budget, trip_type, interests)
        # return the offline response so callers always receive a string
        return offline_response

# Simple offline AI-style response generator (non-AI fallback)-----------------------------------------------------------------------------------------------

def offline_ai_style_response(home_location, destination, days, budget, trip_type, interests):
    vibe = random.choice(["fun", "relaxing", "budget-friendly", "adventurous", "memorable"])

    # helper: parse budget string like '1000000 INR', '50,000', '$800', '800 USD'---------------------------------------
    def parse_budget(budget_str):
        if budget_str is None:
            return 0.0, "₹"
        s = str(budget_str).strip()
        # detect currency
        s_lower = s.lower()
        currency = "INR"
        symbol = "₹"
        if "$" in s or "usd" in s_lower:
            currency = "USD"
            symbol = "$"
        elif "€" in s or "eur" in s_lower:
            currency = "EUR"
            symbol = "€"
        elif "₹" in s or "inr" in s_lower or "rs" in s_lower:
            currency = "INR"
            symbol = "₹"

        # find the first numeric value (allow commas and decimals)
        m = re.search(r"[\d,]+(?:\.\d+)?", s)
        if not m:
            return 0.0, symbol
        num_s = m.group(0).replace(",", "")
        try:
            val = float(num_s)
        except Exception:
            val = 0.0
        return val, symbol
    amount, currency_symbol = parse_budget(budget)
    response = f"""

🌍 **Trip Summary**
A {days}-day {trip_type.lower()} trip from **{home_location}** to **{destination}**, perfect for students looking for a {vibe} experience! 
Enjoy exploring {destination} while keeping your trip within a budget of {currency_symbol}{int(amount):,}.

---

📅 **Day-by-Day Itinerary**
"""
    # Normalize interests: if it's a comma-separated string, split it; if empty, use default
    interest_choices = []
    if interests:
        if isinstance(interests, str):
            # split on commas and newlines and strip whitespace
            interest_choices = [s.strip() for s in re.split(r"[,\n]", interests) if s.strip()]
        elif isinstance(interests, (list, tuple)):
            interest_choices = [str(s).strip() for s in interests if str(s).strip()]

    for i in range(1, days + 1):
        interest = random.choice(interest_choices) if interest_choices else "Local sights"
        response += f"**Day {i}:** Explore top {interest.lower()} attractions and local experiences around {destination}. 🗺️\n"

    # compute numeric daily budget (avoid int() on raw string)
    daily = (amount / days) if days > 0 else amount
    response += f"""
---

💰 **Budget Breakdown (Approximate)**
- Accommodation: {currency_symbol}{int(daily * 0.4):,} per day  
- Food & Drinks: {currency_symbol}{int(daily * 0.3):,} per day  
- Local Travel: {currency_symbol}{int(daily * 0.2):,} per day  
- Miscellaneous: {currency_symbol}{int(daily * 0.1):,} per day  

---

🎒 **Suggested Packing List**
"""
    pack_items = ["Clothes 👕", "Power bank 🔋", "ID card 💳"]
    # Add packing items based on keyword matches in interests (case-insensitive)
    interests_lower = ("\n".join(interest_choices)).lower() if interest_choices else ""
    if "beach" in interests_lower or "beaches" in interests_lower:
        pack_items += ["Sunscreen 🧴", "Swimwear 🩱"]
    if "mountain" in interests_lower or "mountains" in interests_lower:
        pack_items += ["Warm jacket 🧥", "Trekking shoes 👟"]
    if "adventure" in interests_lower:
        pack_items += ["Comfortable shoes 👟", "First-aid kit 🩹"]
    if "culture" in interests_lower:
        pack_items += ["Camera 📸", "Notebook 🗒️"]
    if "food" in interests_lower or "cuisine" in interests_lower:
        pack_items += ["Reusable bottle 💧", "Snacks 🍪"]
    response += "- " + "\n- ".join(pack_items)

    tips = [
        "Use local buses to save money 🚍",
        "Keep some cash handy for small shops 💵",
        "Carry a reusable bottle to stay hydrated 💧",
        "Try local food stalls for authentic taste 🍜",
        "Download offline maps 🗺️"
    ]
    response += f"""

---

💡 **Local Travel Tips**
- {random.choice(tips)}
- {random.choice(tips)}
- {random.choice(tips)}

---

✨ Have a great journey from {home_location} to {destination}! 🌟
"""
    return response



#------------------------------------------------------------------------------------------------------------------------
# User Interface using Streamlit ------------------------------------------------------------------------------------------------------------------------
def main():
    st.set_page_config(page_title="AI Travel Planner", page_icon="🌍")
    st.title("🌍 AI Travel Planner")


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

        # Compute duration from dates (inclusive) and use as default for days input------------------------------------------------------------------------------

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

# form checking:--------------------------------------------------------------------------------------------------------------------------------------------
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
        
# After clicking on Generate My Plane button:-----------------------------------------------------------------------------------------------------------------

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
        # For Downloading the Travel Plane:-----------------------------------------------------------------------------------------------------------------------
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
    
# --- Sidebar feedback UI ---------------------------------------------------------------------------------------------------------------------------------------

with st.sidebar:
        st.header("Feedback")
        feedback_text = st.text_area("Share your feedback or suggestions:", key="feedback_text", height=140)
        if st.button("Submit Feedback", key="submit_feedback"):
            if feedback_text and feedback_text.strip():
                entry = feedback_text.strip()
                # save to session state
                st.session_state.setdefault("feedbacks", []).append(entry)
                # append to file for persistence
                try:
                    with open("feedbacks.txt", "a", encoding="utf-8") as f:
                        f.write(entry + "\n---\n")
                    st.success("Thanks! Your feedback has been submitted.")
                    # clear the text area after submit
                    st.session_state["feedback_text"] = ""
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
  
        st.sidebar.success("Thank you for using the AI Travel Planner!")
# Main :-------------------------------------------------------------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    main()
