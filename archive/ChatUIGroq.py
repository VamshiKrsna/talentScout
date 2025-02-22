import streamlit as st
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os
import json
from utils import (
    sanitize_input,
    validate_email,
    validate_phone,
    save_candidate_data
)
from prompts import (
    SYSTEM_PROMPT,
    create_interview_prompt,
    create_tech_assessment_prompt
)

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="TalentScout Hiring Assistant",
    page_icon="👔"
)

# Initialize Groq client
@st.cache_resource
def get_groq_client():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not found in environment variables")
    return ChatGroq(
        api_key=api_key,
        model="llama-3.3-70b-versatile",
        temperature=0.2
    )

# Main interface
st.title("🤝 TalentScout Hiring Assistant")

# Sidebar setup
with st.sidebar:
    st.header("About")
    st.write("""
    Welcome to TalentScout's AI Hiring Assistant! 
    I'm here to help evaluate candidates for technical positions.
    
    This conversation will cover:
    - Basic Information
    - Technical Experience
    - Skills Assessment
    """)
    
    # Clear chat button
    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.session_state.current_stage = "greeting"
        st.session_state.candidate_data = {}
        st.rerun()

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "current_stage" not in st.session_state:
    st.session_state.current_stage = "greeting"
if "candidate_data" not in st.session_state:
    st.session_state.candidate_data = {}

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Initial greeting
if st.session_state.current_stage == "greeting":
    greeting = """Hello! 👋 I'm the TalentScout AI Hiring Assistant. I'll help evaluate your 
    qualifications for our technical positions. Ready to begin? Please tell me your name to get started."""
    with st.chat_message("assistant"):
        st.markdown(greeting)
    st.session_state.messages.append({"role": "assistant", "content": greeting})
    st.session_state.current_stage = "name"

# User input and response handling
if prompt := st.chat_input("Type your message here..."):
    # Sanitize input
    clean_prompt = sanitize_input(prompt)
    
    # Display user message
    st.session_state.messages.append({"role": "user", "content": clean_prompt})
    with st.chat_message("user"):
        st.markdown(clean_prompt)
    
    try:
        client = get_groq_client()
        
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                # Convert messages to a format compatible with ChatGroq
                messages = [{"role": "system", "content": SYSTEM_PROMPT}]
                
                # Add conversation history
                for msg in st.session_state.messages:
                    if msg["role"] == "user":
                        messages.append({"role": "user", "content": msg["content"]})
                    elif msg["role"] == "assistant":
                        messages.append({"role": "assistant", "content": msg["content"]})
                
                # Generate appropriate prompt based on current stage
                if st.session_state.current_stage == "tech_assessment":
                    prompt_text = create_tech_assessment_prompt(clean_prompt, st.session_state.candidate_data)
                else:
                    prompt_text = create_interview_prompt(clean_prompt, st.session_state.current_stage)
                
                messages.append({"role": "user", "content": prompt_text})
                
                # Generate response
                response = client.invoke(messages)
                
                # Extract response content
                if hasattr(response, 'content'):
                    response_text = response.content
                else:
                    response_text = str(response)
                
                # Process response based on current stage
                if st.session_state.current_stage == "collecting_info":
                    try:
                        info = json.loads(response_text)
                        if validate_email(info.get("email")) and validate_phone(info.get("phone")):
                            st.session_state.candidate_data.update(info)
                            st.session_state.current_stage = "tech_stack"
                    except json.JSONDecodeError:
                        pass
                
                # Add assistant's response to chat history
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response_text
                })
                st.markdown(response_text)
                
                # Save candidate data after each interaction
                if st.session_state.candidate_data:
                    save_candidate_data(st.session_state.candidate_data)
                
    except Exception as e:
        error_message = f"Sorry, I encountered an error: {str(e)}"
        st.error(error_message)
        st.session_state.messages.append({
            "role": "assistant",
            "content": error_message
        })