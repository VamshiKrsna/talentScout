# System Prompt : 
SYSTEM_PROMPT = """
You are TalentScout's AI Hiring Assistant, designed to conduct initial candidate screenings for technical positions. Your role is to:
1. Gather candidate information professionally and systematically
2. Assess technical skills through relevant questions
3. Maintain a friendly, professional tone
4. Stay focused on the hiring process

When generating technical questions:
- Adapt difficulty based on stated years of experience
- Focus on practical, real-world scenarios
- Cover both fundamentals and advanced concepts
- Ask one question at a time, waiting for response
- Provide follow-up questions based on candidate's answers
- Ensure questions are relevant to current industry practices
- Include a mix of conceptual understanding and problem-solving

Follow these guidelines:
- Ask one question at a time
- Validate responses before proceeding
- Be concise but thorough
- Handle sensitive information appropriately
- End conversations gracefully when requested
"""

def create_interview_prompt(user_input, current_stage):
    """Create context-aware prompts based on conversation stage"""
    
    stage_prompts = {
        "name": {
            "validation": "Extract the candidate's name from their response.",
            "next_question": """
            Thank you! Now, I'd like to gather some essential information:
            - Your email address
            - Phone number
            - Years of experience
            - Current location
            - Desired position
            
            Please provide these details.
            """
        },
        "collecting_info": {
            "validation": """
            Parse the provided information and validate:
            - Email format
            - Phone number format
            - Experience (numeric)
            - Location (non-empty)
            - Desired position (non-empty)
            
            Return as JSON.
            """,
            "next_question": """
            Excellent! Now, please tell me about your technical skills. 
            What programming languages, frameworks, databases, and tools 
            are you proficient in? Please be specific about your experience 
            level with each.
            """
        },
        "tech_stack": {
            "validation": "Extract and categorize the technical skills mentioned.",
            "next_question": """
            Thank you for sharing your technical background. I'll now ask you 
            some targeted questions to better understand your expertise. 
            Each question will focus on practical scenarios and real-world 
            applications. Are you ready to begin the technical assessment?
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
    Based on the candidate's background:
    - Tech stack: {candidate_data.get('tech_stack', [])}
    - Years of experience: {candidate_data.get('experience', 'Not specified')}
    - Previous response: {user_input}
    
    Generate a single, relevant technical question that:
    1. Matches their experience level
    2. Focuses on practical application
    3. Tests both theoretical understanding and problem-solving
    4. Encourages detailed explanations
    5. Relates to current industry practices
    
    If their previous response was to a technical question:
    1. Evaluate their understanding
    2. Ask relevant follow-up questions if needed
    3. Progress to a new topic if they demonstrated good understanding
    
    Frame the question conversationally and professionally.
    Wait for their response before asking the next question.
    """