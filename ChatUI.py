import streamlit as st
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os

load_dotenv()

st.set_page_config(
    page_title="TalentScout Hiring Assistant",
    page_icon="👔"
)

@st.cache_resource
def get_groq_client():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not found in environment variables")
    return ChatGroq(api_key=api_key,
                    model = "llama-3.3-70b-versatile",
                    temperature=0.2
                )

st.title("🤝 TalentScout Hiring Assistant")

# Sidebar setup
with st.sidebar:
    st.header("About")
    st.write("""
    Welcome to TalentScout's AI Hiring Assistant! 
    I'm here to help you with your hiring needs.
    """)
    
    # Clear chat button
    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.experimental_rerun()

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input and response handling
if prompt := st.chat_input("How can I help with your hiring needs?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    try:
        client = get_groq_client()
        
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                # Prepare messages for API request
                messages = [
                    {
                        "role": "system",
                        "content": """You are TalentScout's AI Hiring Assistant. 
                        Your goal is to help recruiters and hiring managers find 
                        and evaluate candidates effectively. Be professional, 
                        concise, and focus on providing actionable insights."""
                    }
                ]
                
                messages.extend(st.session_state.messages)
                response = client.invoke(messages)
                
                # Add assistant's response to chat history
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response
                })
                st.markdown(response.content)
                
    except Exception as e:
        error_message = f"Sorry, I encountered an error: {str(e)}"
        st.error(error_message)
        st.session_state.messages.append({
            "role": "assistant",
            "content": error_message
        })