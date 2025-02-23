# PERFECT : ALMOST, It is working well and storing most of the data, need to debug 
# why the model isn't giving a summary based on quiz answers.
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
            "name": "",
            "email": "",
            "phone": "",
            "experience": "",
            "position": "",
            "location": "",
            "tech_stack": [],
            "interview": {
                "questions": [],
                "answers": []
            },
            "evaluation_summary": ""
        }
    if "interview_complete" not in st.session_state:
        st.session_state.interview_complete = False

def extract_candidate_info(response: str, current_data: Dict) -> Dict:
    """Extract candidate information from conversation using AI"""
    extraction_prompt = f"""
    From this conversation message, extract the following information if present:
    1. Name
    2. Email
    3. Phone
    4. Years of experience
    5. Position/role they're applying for
    6. Location
    7. Tech stack/skills mentioned

    Current data: {json.dumps(current_data)}
    Message: {response}

    Return only a JSON object with any new information found. If a field isn't found in the message, don't include it in the JSON.
    """
    
    try:
        response = model.generate_content(extraction_prompt)
        new_info = json.loads(response.text)
        
        # Update current data with new information
        for key, value in new_info.items():
            if value and not current_data.get(key):  # Only update if new value exists and current is empty
                if key == "tech_stack" and isinstance(value, str):
                    current_data[key] = [tech.strip() for tech in value.split(",")]
                else:
                    current_data[key] = value
        
        return current_data
    except:
        return current_data

def generate_evaluation_summary(candidate_data: Dict) -> str:
    """Generate an AI evaluation summary of the candidate"""
    if not candidate_data["experience"] or not candidate_data["tech_stack"]:
        return ""
        
    evaluation_prompt = f"""
    Evaluate the candidate based on:
    
    Background:
    - Experience: {candidate_data['experience']}
    - Position: {candidate_data['position']}
    - Tech Stack: {', '.join(candidate_data['tech_stack']) if isinstance(candidate_data['tech_stack'], list) else candidate_data['tech_stack']}
    
    Interview Performance:
    Questions and Answers:
    {json.dumps(dict(zip(candidate_data['interview']['questions'], candidate_data['interview']['answers'])), indent=2)}

    Provide a SINGLE LINE evaluation summary (maximum 100 characters) that assesses:
    1. Experience relevance
    2. Technical knowledge
    3. Overall suitability
    
    Format: Return only the evaluation summary, nothing else.
    """
    
    try:
        response = model.generate_content(evaluation_prompt)
        return response.text.strip()
    except:
        return ""

def save_candidate_data(data: Dict):
    """Save candidate data to a JSON file with evaluation"""
    # replace None/null values with empty strings
    cleaned_data = data.copy()
    for key in cleaned_data:
        if cleaned_data[key] is None:
            cleaned_data[key] = "" if key != "tech_stack" else []
    
    # generating evaluation summary if we have enough data
    if not cleaned_data["evaluation_summary"]:
        cleaned_data["evaluation_summary"] = generate_evaluation_summary(cleaned_data)
    
    # timestamp for naming file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # creates filename using candidate name or email
    name_part = cleaned_data['name'].replace(' ', '_') if cleaned_data['name'] else cleaned_data['email'].split('@')[0]
    filename = f"{name_part}_{timestamp}_interview.json"
    filename = ''.join(c for c in filename if c.isalnum() or c in ['_', '-', '.'])  
    if not os.path.exists("candidates"):
        os.makedirs("candidates")
    
    filepath = os.path.join("candidates", filename)
    
    # save JSON
    with open(filepath, 'w') as f:
        json.dump(cleaned_data, f, indent=4)

def extract_tech_questions(response: str) -> list:
    """Extract technical questions from AI response"""
    questions = re.findall(r'\d+\.\s*(.*?)(?=\d+\.|$)', response, re.DOTALL)
    return [q.strip() for q in questions if q.strip() and '?' in q]

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
    return """You are an AI Hiring Assistant for TalentScout, a technology recruitment agency. Your name is Ash. You conduct initial screening interviews with candidates in a friendly, conversational manner. Your personality traits:

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
    
    init_session_state()
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    if not st.session_state.messages:
        response = st.session_state.chat.send_message(get_initial_prompt())
        with st.chat_message("assistant"):
            st.write(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})
    
    if user_input := st.chat_input("Type your message here..."):
        with st.chat_message("user"):
            st.write(user_input)
        
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        st.session_state.candidate_data = extract_candidate_info(
            user_input, 
            st.session_state.candidate_data
        )
        
        context = f"""Previous candidate data: {json.dumps(st.session_state.candidate_data)}
        Remember to:
        1. Acknowledge any information shared
        2. Ask for missing information naturally
        3. Generate technical questions if tech stack is provided and questions haven't been asked
        4. Mark interview as complete by saying "INTERVIEW COMPLETE" if:
           - All basic information is collected
           - At least 3 technical questions have been asked and answered
        5. Stay conversational and friendly
        6. Number your technical questions (1., 2., 3.)"""
        
        # get gemini response
        response = st.session_state.chat.send_message(
            f"{context}\n\nUser message: {user_input}"
        )
        
        # Extract technical questions
        questions = extract_tech_questions(response.text)
        if questions:
            st.session_state.candidate_data["interview"]["questions"].extend(questions)
        
        # if this is an answer to a technical question, store it
        if st.session_state.candidate_data["interview"]["questions"] and len(st.session_state.candidate_data["interview"]["questions"]) > len(st.session_state.candidate_data["interview"]["answers"]):
            st.session_state.candidate_data["interview"]["answers"].append(user_input)
        
        with st.chat_message("assistant"):
            st.write(response.text)
        
        st.session_state.messages.append({"role": "assistant", "content": response.text})
        
        # Check for INTERVIEW COMPLETE flag and save the data to JSON
        if "INTERVIEW COMPLETE" in response.text and not st.session_state.interview_complete:
            save_candidate_data(st.session_state.candidate_data)
            st.session_state.interview_complete = True

if __name__ == "__main__":
    main()