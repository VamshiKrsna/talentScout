import re

def sanitize_input(input_text):
    """Sanitize user input to prevent injection attacks."""
    return input_text.strip()

def validate_email(email):
    """Validate email format."""
    regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(regex, email) is not None

def validate_phone(phone):
    """Validate phone number format."""
    regex = r'^\+?[1-9]\d{1,14}$'  # E.164 format
    return re.match(regex, phone) is not None

def save_candidate_data(candidate_data):
    """Save candidate data to a JSON file."""
    with open("candidate_data.json", "w") as f:
        json.dump(candidate_data, f)