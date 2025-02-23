import streamlit as st
import google.generativeai as genai
import json
from datetime import datetime
import os
from typing import Dict
import re
from dotenv import load_dotenv

load_dotenv()

# config gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

# initialzing the model
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
            "interview": {
                "questions": [],
                "answers": []
            },
            "evaluation_summary": None
        }
    if "interview_complete" not in st.session_state:
        st.session_state.interview_complete = False

def generate_evaluation_summary(candidate_data: Dict) -> str:
    """Generate an AI evaluation summary of the candidate"""
    evaluation_prompt = f"""
    Based on the candidate's information:
    - Experience: {candidate_data['experience']}
    - Position: {candidate_data['position']}
    - Tech Stack: {candidate_data['tech_stack']}
    - Interview Questions: {json.dumps(candidate_data['interview']['questions'])}
    - Interview Answers: {json.dumps(candidate_data['interview']['answers'])}

    Provide a single-line evaluation summary (max 100 characters) that considers:
    1. Experience relevance to position
    2. Technical knowledge demonstrated
    3. Overall fit for the role
    
    Format: Just return the evaluation summary, nothing else.
    """
    
    response = model.generate_content(evaluation_prompt)
    return response.text.strip()

def extract_info_from_response(response: str, candidate_data: Dict) -> Dict:
    """Extract and validate information from responses"""
    # verify and look for email
    email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', response)
    if email_match and candidate_data["email"] is None:
        email = email_match.group(0)
        if validate_email(email):
            candidate_data["email"] = email

    # verify and look for phone number
    phone_match = re.search(r'\+?1?\d{9,15}', response)
    if phone_match and candidate_data["phone"] is None:
        phone = phone_match.group(0)
        if validate_phone(phone):
            candidate_data["phone"] = phone

    return candidate_data

def extract_tech_questions(response: str) -> str:
    """Extract technical questions from AI response"""
    # Look for numbered questions in the response
    questions = re.findall(r'\d+\.\s*(.*?(?=\d+\.|$))', response, re.DOTALL)
    return [q.strip() for q in questions if q.strip()]

def save_candidate_data(data: Dict):
    """Save candidate data to a JSON file with evaluation"""
    # generating evaluation summary if interview is complete
    if data["tech_stack"] and data["interview"]["answers"]:
        data["evaluation_summary"] = generate_evaluation_summary(data)
    
    # timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # creating filename using candidate name if available, otherwise use timestamp
    name_part = data['name'].replace(' ', '_') if data['name'] else 'unnamed_candidate'
    filename = f"candidate_{name_part}_{timestamp}.json"
    
    if not os.path.exists("candidates"):
        os.makedirs("candidates")
    
    filepath = os.path.join("candidates", filename)
    
    # saving JSON
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=4)

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
2. When asking technical questions, always number them (1., 2., 3.)
3. Maintain context and remember information shared
4. If you detect an email or phone number in responses, validate their format
5. Generate 3 basic technical questions based on their tech stack when appropriate
6. After collecting all technical responses, indicate "INTERVIEW COMPLETE" in your response
7. Make sure to collect specific years of experience and clear position title

Always be conversational and natural, while subtly guiding the conversation to gather required information.

Begin by introducing yourself and asking for the candidate's name."""

def validate_email(email: str) -> bool:
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_phone(phone: str) -> bool:
    pattern = r'^\+?1?\d{9,15}$'
    return bool(re.match(pattern, phone))

def main():
    st.title("TalentScout Hiring Assistant")
    
    # intializing chat session state
    init_session_state()
    
    # displaying chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    # If first message, send the initial prompt
    if not st.session_state.messages:
        response = st.session_state.chat.send_message(get_initial_prompt())
        with st.chat_message("assistant"):
            st.write(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})
    
    # user input
    if user_input := st.chat_input("Type your message here..."):
        with st.chat_message("user"):
            st.write(user_input)
        
        # adding user message to history
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        st.session_state.candidate_data = extract_info_from_response(
            user_input, 
            st.session_state.candidate_data
        )
        
        # contextual prompt for Gemini
        context = f"""Previous candidate data: {json.dumps(st.session_state.candidate_data)}
        Remember to:
        1. Acknowledge any information shared
        2. Ask for missing information naturally
        3. Generate technical questions if tech stack is provided and questions haven't been asked
        4. Mark interview as complete if all information is gathered and technical questions are answered
        5. Stay conversational and friendly
        6. Number your technical questions (1., 2., 3.)"""
        
        # AI responses
        response = st.session_state.chat.send_message(
            f"{context}\n\nUser message: {user_input}"
        )
        
        # extract technical questions if present in response
        questions = extract_tech_questions(response.text)
        if questions:
            st.session_state.candidate_data["interview"]["questions"].extend(questions)
        
        #  if answered to a technical question, store it
        if st.session_state.candidate_data["interview"]["questions"] and len(st.session_state.candidate_data["interview"]["questions"]) > len(st.session_state.candidate_data["interview"]["answers"]):
            st.session_state.candidate_data["interview"]["answers"].append(user_input)
        
        with st.chat_message("assistant"):
            st.write(response.text)
        
        st.session_state.messages.append({"role": "assistant", "content": response.text})
        
        # check for INTERVIEW COMPLETE Flag and save data if found
        if "INTERVIEW COMPLETE" in response.text and not st.session_state.interview_complete:
            save_candidate_data(st.session_state.candidate_data)
            st.session_state.interview_complete = True

if __name__ == "__main__":
    main()