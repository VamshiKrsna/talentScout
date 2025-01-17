SYSTEM_PROMPT = """
You are TalentScout's AI Hiring Assistant, here to conduct friendly and professional candidate screenings for technical positions. Your role is to:
1. Gather candidate information step by step, asking only one question at a time.
2. Assess technical skills by tailoring questions to the candidate's stated tech stack and experience.
3. Maintain a conversational, approachable tone while keeping the focus on hiring goals.
4. Adapt your questions to the candidate's responses to create a smooth, engaging interview process.

When generating technical questions:
- Match the difficulty to the candidate’s experience level.
- Focus on practical applications, real-world scenarios, and industry relevance.
- Combine fundamental and advanced topics, and ensure clarity in your questions.
- Ask one question at a time and wait for the candidate’s response before continuing.
- If needed, provide follow-up questions based on the candidate's answers.
- Keep all interactions concise, friendly, and relevant to the hiring process.

Guidelines:
- Validate all provided information (e.g., email, phone) and handle errors politely.
- Save the candidate's details, responses, and performance analysis to a file securely after the interview.
- End the conversation with a warm, professional thank-you message.
"""

def create_interview_prompt(user_input, current_stage):
    """Generate prompts for gathering candidate information in stages."""
    stage_prompts = {
        "name": {
            "validation": "Extract the candidate's name from their response.",
            "next_question": """
            Thank you! It's great to meet you. Could you please share your email address so we can stay in touch? 
            """
        },
        "email": {
            "validation": "Validate the email format provided by the candidate.",
            "next_question": """
            Thanks for sharing your email! May I have your phone number as well? This will help us contact you when needed.
            """
        },
        "phone": {
            "validation": "Validate the phone number format provided by the candidate.",
            "next_question": """
            Excellent! How many years of professional experience do you have? A rough estimate works!
            """
        },
        "experience": {
            "validation": "Ensure the years of experience provided are valid (numeric).",
            "next_question": """
            That’s great to know. Could you please share your current location (city, state, or country)?
            """
        },
        "location": {
            "validation": "Ensure the location is not empty.",
            "next_question": """
            Fantastic! Lastly, what position are you interested in? Feel free to mention any specific roles or areas of focus.
            """
        },
        "position": {
            "validation": "Ensure the desired position is valid and non-empty.",
            "next_question": """
            Thank you for providing your details! Let's now dive into your technical skills. Could you list the programming languages, frameworks, and tools you're proficient in? 
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
    """Generate technical assessment questions based on declared skills."""
    return f"""
    Based on the candidate's background:
    - Tech stack: {', '.join(candidate_data.get('tech_stack', [])) if candidate_data.get('tech_stack') else "No tech stack provided yet"}
    - Years of experience: {candidate_data.get('experience', 'Not specified')}
    
    Generate one targeted technical question that:
    1. Matches their experience level
    2. Tests practical application and problem-solving skills
    3. Encourages a detailed but approachable explanation
    4. Relates to current industry standards and practices
    
    If they answered a previous question:
    1. Evaluate their response in a friendly and supportive tone.
    2. If their answer was strong, ask a new question on a different topic.
    3. If their answer needs clarification, ask a follow-up question to dig deeper.
    
    Frame the question conversationally and wait for their response before continuing.
    """