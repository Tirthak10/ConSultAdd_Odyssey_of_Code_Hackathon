import groq
import os
from dotenv import load_dotenv
import json

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

def check_eligibility(company_data, rfp_chunks):
    """
    Check if the company is eligible for the RFP using LLM
    Args:
        company_data: Dictionary containing structured company information
        rfp_chunks: List of relevant RFP text chunks
    Returns:
        Detailed eligibility analysis
    """
    # Prepare company data context
    company_context = json.dumps(company_data, indent=2)
    
    # Combine RFP chunks
    rfp_context = "RFP Requirements:\n"
    for chunk in rfp_chunks:
        if isinstance(chunk, dict):
            rfp_context += chunk.get('text', '') + '\n'
        else:
            rfp_context += chunk + '\n'

    # Generate eligibility analysis using LLM
    prompt = """
    Analyze the company's eligibility for this RFP by comparing company data against requirements.
    
    Evaluate these aspects:
    1. Business Qualifications
       - Registration status
       - Years in business
       - Required certifications
    
    2. Technical Capabilities
       - Required expertise
       - Past performance
       - Team qualifications
    
    3. Compliance Status
       - Required licenses
       - Insurance coverage
       - Regulatory compliance
    
    4. Financial Requirements
       - Revenue thresholds
       - Financial stability
       - Insurance requirements
    
    Provide:
    1. Clear GO/NO-GO determination
    2. Detailed justification for each major requirement
    3. List of any gaps or concerns
    4. Recommendations if improvements needed
    
    Format with clear sections and highlight the final determination prominently.
    """

    try:
        response = client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=[
                {
                    "role": "system", 
                    "content": "You are an expert in government contracting and RFP analysis. Provide clear, actionable eligibility determinations."
                },
                {
                    "role": "user", 
                    "content": f"Company Data:\n{company_context}\n\nRFP Information:\n{rfp_context}\n\n{prompt}"
                }
            ],
            temperature=0.3,
            max_tokens=2000
        )
        
        return response.choices[0].message.content
    except Exception as e:
        return f"Error analyzing eligibility: {str(e)}"
