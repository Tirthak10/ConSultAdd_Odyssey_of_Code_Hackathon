import groq
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_groq_client():
    """Initialize and return Groq client with proper configuration"""
    api_key = os.getenv('GROQ_API_KEY')
    if not api_key:
        raise ValueError("GROQ_API_KEY environment variable is not set")
    return groq.Client(api_key=api_key)

# Initialize client
client = get_groq_client()

def generate_checklist(data):
    """
    Generate a compliance checklist analysis using LLM
    """
    # Extract data
    company_data = data.get('company_data', {})
    rfp_summary = data.get('rfp_summary', '')

    # Prepare context
    context = f"""
    RFP Summary:
    {rfp_summary}

    Company Information:
    {str(company_data)}
    """

    # Generate compliance analysis using LLM
    prompt = """
    Analyze the company's compliance status against standard requirements and RFP specifications.
    Focus on these key areas:

    1. General Legal and Regulatory Compliance
    2. Required Licensing, Permits, and Certifications
    3. Insurance Coverage Requirements
    4. Data Protection and Privacy Compliance
    5. Labor and Employment Compliance
    6. Tax Compliance Status
    7. Anti-Corruption and Ethical Conduct Policies
    8. Intellectual Property Rights
    9. Proposal and Contractual Compliance

    For each area:
    - Identify if the company meets the requirements (Met/Not Met/Partially Met)
    - Provide specific findings and evidence
    - List any gaps or concerns
    - Suggest required actions for compliance

    Format the response with clear sections and status indicators.
    """

    try:
        response = client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=[
                {"role": "system", "content": "You are an expert in compliance analysis and government contracting requirements."},
                {"role": "user", "content": f"{prompt}\n\nContext:\n{context}"}
            ],
            temperature=0.3,
            max_tokens=2000
        )
        
        return response.choices[0].message.content
    except Exception as e:
        return f"Error generating compliance analysis: {str(e)}"
