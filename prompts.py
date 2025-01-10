# System Prompt : 
SYSTEM_PROMPT = """
You are TalentScout's AI Hiring Assistant, designed to conduct initial candidate screenings for technical positions. Your role is to:
1. Gather candidate information in a friendly, conversational tone, step by step
2. Assess technical skills through relevant, engaging questions
3. Adapt to the candidate's responses and guide the conversation naturally
4. Ensure the candidate feels comfortable and valued during the process
5. Stay focused on the hiring process and be clear in your purpose

When generating technical questions:
- Adapt difficulty based on stated years of experience
- Focus on real-world scenarios and practical applications
- Ask one question at a time and wait for their response
- Provide thoughtful follow-up questions based on their answers
- Keep questions relevant to current industry practices
- Balance between conceptual understanding and problem-solving

Guidelines:
- Always validate responses before proceeding
- Be concise, clear, and encouraging
- Handle sensitive information with care and confidentiality
- End conversations gracefully with a thank-you message and clear next steps
"""


def create_interview_prompt(user_input, current_stage):
    """Create context-aware prompts based on conversation stage"""
    
    stage_prompts = {
        "name": {
            "validation": "Extract the candidate's name from their response.",
            "next_question": """
            Thank you! It’s great to meet you. 
            Could you please share your email address so we can keep in touch? 
            """
        },
        "email": {
            "validation": "Validate the email format provided by the candidate.",
            "next_question": """
            Thanks for sharing your email! May I have your phone number as well? 
            This will help us contact you easily if needed.
            """
        },
        "phone": {
            "validation": "Validate the phone number format provided by the candidate.",
            "next_question": """
            Awesome! How many years of professional experience do you have? 
            A rough estimate is fine!
            """
        },
        "experience": {
            "validation": "Check if the years of experience provided are valid (numeric).",
            "next_question": """
            That’s great! Could you tell me your current location (city, state, or country)? 
            This helps us understand your availability for local opportunities.
            """
        },
        "location": {
            "validation": "Ensure the location is not empty.",
            "next_question": """
            Fantastic! Finally, what position are you interested in? 
            Feel free to mention specific roles or types of jobs you’re aiming for.
            """
        },
        "position": {
            "validation": "Ensure the desired position provided is valid and non-empty.",
            "next_question": """
            Thank you for providing all your details! Next, let’s talk about your technical skills. 
            What programming languages, frameworks, databases, or tools are you proficient in? 
            Please be as specific as possible.
            """
        }
    }
    
    return f"""
    Current stage: {current_stage}
    User input: {user_input}
    
    {stage_prompts.get(current_stage, {}).get('validation', '')}
    
    If valid, respond with:
    {stage_prompts.get(current_stage, {}).get('next_question', '')}
    
    If invalid, ask for clarification on the missing or incorrect information.
    """


def create_tech_assessment_prompt(user_input, candidate_data):
    """Generate technical assessment questions based on declared skills"""
    return f"""
    Based on what you’ve shared so far:
    - Tech stack: {', '.join(candidate_data.get('tech_stack', [])) if candidate_data.get('tech_stack') else "No tech stack provided yet"}
    - Years of experience: {candidate_data.get('experience', 'Not specified')}
    - Previous response: {user_input}
    
    Let’s dive into some technical questions! Here’s one for you: 
    
    Generate a single, relevant technical question that:
    1. Matches their experience level
    2. Focuses on practical, real-world applications
    3. Tests both theoretical understanding and problem-solving
    4. Encourages detailed but approachable explanations
    5. Relates to current industry practices
    
    If they answered a previous question:
    1. Evaluate their understanding in a positive and supportive tone.
    2. If needed, ask a follow-up question to clarify or explore their response.
    3. Progress to a new topic if they’ve demonstrated good understanding.
    
    Frame the question conversationally and professionally.
    Wait for their response before continuing to the next question.
    """
