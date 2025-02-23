# This Python script was offering better conversationality 
# but cannot be used due as it doesn't save json data.

import streamlit as st
import google.generativeai as genai
import json
from datetime import datetime
import os
from typing import Dict
import re
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

# Initialize the model
model = genai.GenerativeModel('gemini-pro')

def init_session_state():
    """Initialize session state variables"""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "chat" not in st.session_state:
        st.session_state.chat = model.start_chat(history=[])
    if "candidate_data" not in st.session_state:
        st.session_state.candidate_data = {
            "name": None,
            "email": None,
            "phone": None,
            "experience": None,
            "position": None,
            "location": None,
            "tech_stack": None,
            "technical_responses": []
        }
    if "interview_complete" not in st.session_state:
        st.session_state.interview_complete = False

def get_initial_prompt() -> str:
    return """You are an AI Hiring Assistant for TalentScout, a technology recruitment agency. Your name is Alex. You conduct initial screening interviews with candidates in a friendly, conversational manner. Your personality traits:

1. Professional yet warm and approachable
2. Patient and understanding
3. Clear communicator
4. Able to keep conversations on track while being natural

Your goals during the conversation:
1. Collect candidate information: name, email, phone, experience, desired position, location, and tech stack
2. Ask relevant technical questions based on their tech stack
3. Maintain a natural conversation flow while gathering required information
4. Answer any questions about the company or process
5. Keep technical questions simple and straightforward

Important rules:
1. Stay in character as Alex the hiring assistant
2. Maintain context and remember information shared
3. If you detect an email or phone number in responses, validate their format
4. Generate 3 basic technical questions based on their tech stack when appropriate
5. Mark the interview as complete after collecting all required information and technical responses

Always be conversational and natural, while subtly guiding the conversation to gather required information.

Begin by introducing yourself and asking for the candidate's name."""

def validate_email(email: str) -> bool:
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_phone(phone: str) -> bool:
    pattern = r'^\+?1?\d{9,15}$'
    return bool(re.match(pattern, phone))

def extract_info_from_response(response: str, candidate_data: Dict) -> Dict:
    """Extract and validate information from responses"""
    # Look for email
    email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', response)
    if email_match and candidate_data["email"] is None:
        email = email_match.group(0)
        if validate_email(email):
            candidate_data["email"] = email

    # Look for phone
    phone_match = re.search(r'\+?1?\d{9,15}', response)
    if phone_match and candidate_data["phone"] is None:
        phone = phone_match.group(0)
        if validate_phone(phone):
            candidate_data["phone"] = phone

    return candidate_data

def save_candidate_data(data: Dict):
    """Save candidate data to a JSON file"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"candidate_{data['name'].replace(' ', '_')}_{timestamp}.json"
    
    if not os.path.exists("candidates"):
        os.makedirs("candidates")
    
    filepath = os.path.join("candidates", filename)
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=4)

def main():
    st.title("TalentScout Hiring Assistant")
    
    # Initialize session state
    init_session_state()
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    # If it's the first message, send the initial prompt
    if not st.session_state.messages:
        response = st.session_state.chat.send_message(get_initial_prompt())
        with st.chat_message("assistant"):
            st.write(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})
    
    # Get user input
    if user_input := st.chat_input("Type your message here..."):
        # Display user message
        with st.chat_message("user"):
            st.write(user_input)
        
        # Add user message to history
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # Extract information from user input
        st.session_state.candidate_data = extract_info_from_response(
            user_input, 
            st.session_state.candidate_data
        )
        
        # Generate contextual prompt for Gemini
        context = f"""Previous candidate data: {json.dumps(st.session_state.candidate_data)}
        Remember to:
        1. Acknowledge any information shared
        2. Ask for missing information naturally
        3. Generate technical questions if tech stack is provided and questions haven't been asked
        4. Mark interview as complete if all information is gathered and technical questions are answered
        5. Stay conversational and friendly"""
        
        # Get AI response
        response = st.session_state.chat.send_message(
            f"{context}\n\nUser message: {user_input}"
        )
        
        # Display assistant response
        with st.chat_message("assistant"):
            st.write(response.text)
        
        # Add assistant response to history
        st.session_state.messages.append({"role": "assistant", "content": response.text})
        
        # Check if interview is complete and save data
        if "interview complete" in response.text.lower() and not st.session_state.interview_complete:
            save_candidate_data(st.session_state.candidate_data)
            st.session_state.interview_complete = True

if __name__ == "__main__":
    main()