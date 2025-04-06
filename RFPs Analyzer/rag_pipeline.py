from utils.vector_store import retrieve_chunks, store_chunks, get_document_metadata
from utils.embedding import generate_embeddings
from utils.text_cleaner import preprocess_file
from agents.eligibility_agent import check_eligibility
from agents.checklist_agent import generate_checklist
from agents.risk_analysis_agent import analyze_risks
import groq
import os
import json
from dotenv import load_dotenv
from datetime import datetime

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

def process_documents(rfp_file, company_data=None):
    """
    Process RFP and company data through the RAG pipeline
    Args:
        rfp_file: The RFP document file
        company_data: Company profile data (dict or file)
    Returns:
        tuple: (success_status, response_data)
    """
    try:
        # Process RFP document
        rfp_chunks = preprocess_file(rfp_file)
        rfp_embeddings = generate_embeddings(rfp_chunks)
        
        # Store RFP chunks
        rfp_metadata = {
            'filename': rfp_file.filename,
            'upload_time': datetime.now().isoformat(),
            'document_type': 'rfp'
        }
        doc_id = store_chunks(rfp_embeddings, rfp_file.filename, rfp_metadata)
        
        # Generate RFP summary
        summary_prompt = """
        Provide a concise summary of the RFP document covering:
        1. Key requirements and objectives
        2. Timeline and critical deadlines
        3. Technical specifications
        4. Evaluation criteria
        5. Compliance requirements
        """
        
        context = " ".join([chunk['text'] for chunk in rfp_embeddings[:3]])
        
        summary = client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=[
                {"role": "system", "content": "You are an expert in analyzing RFP documents."},
                {"role": "user", "content": f"{summary_prompt}\n\nContext:\n{context}"}
            ],
            temperature=0.3,
            max_tokens=1000
        )
        
        # Process company data if provided
        company_info = None
        if company_data:
            if isinstance(company_data, dict):
                company_info = company_data
            elif hasattr(company_data, 'read'):
                try:
                    company_info = json.load(company_data)
                except json.JSONDecodeError:
                    content = company_data.read().decode('utf-8')
                    company_info = parse_company_text(content)
        
        # Generate analysis results
        results = {
            "rfp_doc_id": doc_id,
            "summary": summary.choices[0].message.content,
            "chunks_processed": len(rfp_embeddings)
        }
        
        if company_info:
            # Perform eligibility check
            eligibility_result = check_eligibility(company_info, rfp_chunks)
            results["eligibility"] = eligibility_result
            
            # Generate compliance checklist
            checklist_result = generate_checklist({
                "company_data": company_info,
                "rfp_summary": results["summary"]
            })
            results["compliance"] = checklist_result
            
            # Analyze risks
            risk_result = analyze_risks(rfp_chunks, company_info)
            results["risks"] = risk_result
        
        return True, results
        
    except Exception as e:
        return False, f"Error processing documents: {str(e)}"

def parse_company_text(content):
    """Parse structured text into company data dictionary"""
    data = {}
    current_section = "general"
    
    for line in content.split('\n'):
        line = line.strip()
        if not line:
            continue
            
        if line.endswith(':'):
            current_section = line[:-1].lower()
            data[current_section] = {}
        elif ':' in line:
            key, value = line.split(':', 1)
            if current_section not in data:
                data[current_section] = {}
            data[current_section][key.strip().lower()] = value.strip()
        else:
            if current_section not in data:
                data[current_section] = []
            data[current_section].append(line)
            
    return data

def process_query(query):
    """Process a natural language query about the RFP"""
    query_embedding = generate_embeddings([query])[0]['embedding']
    relevant_chunks = retrieve_chunks(query_embedding)
    context = " ".join([chunk['text'] for chunk in relevant_chunks])

    response = client.chat.completions.create(
        model="mixtral-8x7b-32768",
        messages=[
            {"role": "system", "content": "You are an expert in analyzing RFP documents. Use the provided context to answer questions accurately and concisely."},
            {"role": "user", "content": f"Context: {context}\n\nQuestion: {query}"}
        ],
        temperature=0.5,
        max_tokens=1000
    )
    
    return response.choices[0].message.content
