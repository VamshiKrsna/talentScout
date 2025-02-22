import streamlit as st
import google.generativeai as genai
import json
import os
from datetime import datetime
from templates import SYSTEM_PROMPT

# Configure Gemini with API Key
def configure_gemini(api_key):
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-pro')

# Initialize UI session state
def init_session():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "data" not in st.session_state:
        st.session_state.data = {
            "profile": {},
            "qa": []
        }

# save candidate data
def save_data(name):
    sanitized_name = "".join(c for c in name if c.isalnum())
    filename = f"candidates/{sanitized_name}_{datetime.now().strftime('%Y%m%d%H%M')}.json"
    
    os.makedirs("candidates", exist_ok=True)
    with open(filename, "w") as f:
        json.dump(st.session_state.data, f, indent=2)
    
    # Secure file permissions
    os.chmod(filename, 0o600)

# processing user input
def process_input(prompt, model):
    try:
        response = model.generate_content(SYSTEM_PROMPT + "\n\nChat History:\n" + 
                   "\n".join([f"{msg['role']}: {msg['content']}" for msg in st.session_state.messages]))
        
        if response.text.startswith("[Question]"):
            st.session_state.data["qa"].append({
                "question": response.text.split("]")[1].strip(),
                "answer": prompt
            })
        elif response.text.startswith("[Greeting]"):
            st.session_state.messages.append({"role": "assistant", "content": response.text.split("]")[1].strip()})
        elif response.text.startswith("[End]"):
            save_data(st.session_state.data["profile"].get("name", "unknown"))
            st.session_state.messages.append({"role": "assistant", "content": "Thank you! Your application is complete."})
            st.rerun()
        else:
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        
    except Exception as e:
        st.error(f"Error processing request: {str(e)}")

# Streamlit UI
def main():
    st.title("TalentMate Hiring Assistant")
    st.markdown("All data is encrypted and stored securely")
    
    api_key = st.sidebar.text_input("Enter Gemini API Key:", type="password")
    
    if not api_key:
        st.info("Please enter your Gemini API key to continue")
        return
    
    model = configure_gemini(api_key)
    init_session()
    
    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])
    
    if prompt := st.chat_input("Type your response here..."):
        st.chat_message("user").write(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # extracting info from user inputs
        if len(st.session_state.messages) == 1:
            fields = ["name", "email", "phone", "experience", "position", "location", "tech_stack"]
            current_field = fields[len(st.session_state.data["profile"])]
            
            if current_field == "tech_stack":
                st.session_state.data["profile"]["tech_stack"] = [t.strip() for t in prompt.split(",")]
            else:
                st.session_state.data["profile"][current_field] = prompt
        
        with st.spinner("Processing..."):
            process_input(prompt, model)
        
        st.rerun()

if __name__ == "__main__":
    main()