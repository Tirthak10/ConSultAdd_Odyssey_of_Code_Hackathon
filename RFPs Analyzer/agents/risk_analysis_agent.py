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

def analyze_risks(chunks, company_data=None):
    """
    Analyze potential risks in the RFP using LLM
    """
    # Combine relevant RFP sections and company data
    context = "RFP Content:\n"
    for chunk in chunks:
        if isinstance(chunk, dict):
            context += chunk.get('text', '') + '\n'
        else:
            context += chunk + '\n'
            
    if company_data:
        context += f"\nCompany Profile:\n{str(company_data)}"

    # Generate risk analysis using LLM
    prompt = """
    Analyze the RFP for potential risks and challenges. Consider:
    1. Technical Risks
       - Technology complexity and requirements
       - Integration challenges
       - Resource capabilities
       - Performance requirements

    2. Business Risks
       - Contract value vs. capacity
       - Resource allocation
       - Market competition
       - Strategic alignment

    3. Financial Risks
       - Project profitability
       - Cash flow requirements
       - Payment terms
       - Cost overrun potential

    4. Operational Risks
       - Timeline feasibility
       - Resource availability
       - Supply chain dependencies
       - Quality control requirements

    5. Compliance Risks
       - Regulatory requirements
       - Certification needs
       - Data security requirements
       - Legal obligations
    
    For each identified risk:
    - Describe the risk and its potential impact
    - Rate the severity (High/Medium/Low)
    - Rate the probability (High/Medium/Low)
    - Provide specific mitigation strategies
    - Suggest contingency plans

    Format the response with:
    1. Executive Summary
    2. Detailed Risk Analysis by Category
    3. Risk Matrix
    4. Top Priority Risks
    5. Recommended Actions
    """

    try:
        response = client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=[
                {"role": "system", "content": "You are an expert in risk analysis for government contracts and RFPs."},
                {"role": "user", "content": f"{prompt}\n\nContext:\n{context}"}
            ],
            temperature=0.3,
            max_tokens=2000
        )
        
        return response.choices[0].message.content
    except Exception as e:
        return f"Error analyzing risks: {str(e)}"
