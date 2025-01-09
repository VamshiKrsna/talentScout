import re
import json
from datetime import datetime
import os

def sanitize_input(text):
    """Removes any harmful operators from input (that might trick the llm and prompt)"""
    return re.sub(r'[<>&;]', '', text)

def validate_email(email):
    """Validates email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, str(email)))

def validate_phone(phone):
    """Validates phone number format"""
    pattern = r'^\+?1?\d{9,15}$'
    return bool(re.match(pattern, str(phone)))

def save_candidate_data(data):
    """Saves candidate data securely"""
    if not os.path.exists('data'):
        os.makedirs('data')
        
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"data/candidate_{timestamp}.json"
    
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)