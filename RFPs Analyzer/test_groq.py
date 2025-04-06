import groq
import os
from dotenv import load_dotenv

def get_groq_client():
    """Initialize and return Groq client with proper configuration"""
    api_key = os.getenv('GROQ_API_KEY')
    if not api_key:
        raise ValueError("GROQ_API_KEY environment variable is not set")
    return groq.Client(api_key=api_key)

def test_groq_connection():
    try:
        # Load environment variables
        load_dotenv()
        
        # Initialize Groq client
        client = get_groq_client()
        
        # Test API call
        response = client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Please respond with 'Groq LLM is working!' if you receive this message."}
            ],
            temperature=0.3,
            max_tokens=100
        )
        
        print("API Response:", response.choices[0].message.content)
        print("\nConnection Test: SUCCESS ✅")
        return True
        
    except Exception as e:
        print(f"\nConnection Test: FAILED ❌")
        print(f"Error: {str(e)}")
        return False

if __name__ == "__main__":
    print("Testing Groq LLM connection...")
    test_groq_connection()