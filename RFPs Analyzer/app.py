from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
from rag_pipeline import process_documents, process_query
from agents.eligibility_agent import check_eligibility
from agents.checklist_agent import generate_checklist
from agents.risk_analysis_agent import analyze_risks
from utils.text_cleaner import preprocess_file
from utils.json_converter import RFPJsonConverter
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Make UPLOAD_FOLDER an absolute path
UPLOAD_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), "uploads"))
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Initialize JSON converter
json_converter = RFPJsonConverter()

def process_company_data(file):
    """Process company data from PDF or DOCX format"""
    try:
        # Use the same preprocess_file function that handles PDFs and DOCX
        chunks = preprocess_file(file)
        # Join all chunks into a single text
        text_content = ' '.join(chunks)
        
        # Create a structured format from the extracted text
        data = {
            "document_text": text_content,
            "file_name": file.filename,
            "file_type": file.filename.split('.')[-1].lower()
        }
        return data
    except Exception as e:
        print(f"Error processing company data: {e}")
        return None

@app.route('/upload', methods=['POST'])
def upload_files():
    rfp_file = request.files.get('rfp')

    if not rfp_file:
        return jsonify({"error": "RFP file is required"}), 400

    try:
        # Save file temporarily
        rfp_path = os.path.join(app.config['UPLOAD_FOLDER'], rfp_file.filename)
        rfp_file.save(rfp_path)
        
        # Process documents through RAG pipeline
        success, result = process_documents(rfp_file)
        
        if not success:
            return jsonify({"error": result}), 500
            
        return jsonify({
            "message": "File processed successfully",
            "result": result
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/analyze', methods=['POST'])
def analyze_documents():
    """
    Analyze RFP document and company data.
    Both files can be in PDF or DOCX format
    """
    if 'rfp' not in request.files or 'company_data' not in request.files:
        return jsonify({"error": "Both RFP and company data files are required"}), 400

    rfp_file = request.files['rfp']
    company_data_file = request.files['company_data']

    if not rfp_file.filename or not company_data_file.filename:
        return jsonify({"error": "No file selected"}), 400

    # Validate file extensions
    allowed_extensions = {'pdf', 'docx'}
    if not all(f.filename.lower().endswith(tuple(f'.{ext}' for ext in allowed_extensions)) 
              for f in [rfp_file, company_data_file]):
        return jsonify({"error": "Files must be in PDF or DOCX format"}), 400

    try:
        # Save files temporarily
        rfp_path = os.path.join(app.config['UPLOAD_FOLDER'], rfp_file.filename)
        company_path = os.path.join(app.config['UPLOAD_FOLDER'], company_data_file.filename)
        
        rfp_file.save(rfp_path)
        company_data_file.save(company_path)

        # Process company data
        company_data = process_company_data(company_data_file)
        if not company_data:
            return jsonify({"error": "Failed to process company data"}), 500

        # Process documents through RAG pipeline
        success, results = process_documents(rfp_file, company_data)
        
        if not success:
            return jsonify({"error": results}), 500

        # Clean up temporary files
        os.remove(rfp_path)
        os.remove(company_path)

        return jsonify(results), 200

    except Exception as e:
        # Clean up files in case of error
        for path in [rfp_path, company_path]:
            if os.path.exists(path):
                os.remove(path)
        return jsonify({"error": str(e)}), 500

@app.route('/query', methods=['POST'])
def query_documents():
    """
    Process natural language queries about the RFP
    """
    query = request.json.get('query')
    if not query:
        return jsonify({"error": "Query is required"}), 400

    try:
        result = process_query(query)
        return jsonify({"result": result}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/convert-to-json', methods=['POST'])
def convert_rfp_to_json():
    """Convert RFP document to structured JSON format"""
    if 'rfp' not in request.files:
        return jsonify({"error": "RFP file is required"}), 400

    rfp_file = request.files['rfp']
    if not rfp_file.filename:
        return jsonify({"error": "No file selected"}), 400

    # Validate file extension
    if not rfp_file.filename.lower().endswith(('.pdf', '.docx')):
        return jsonify({"error": "File must be in PDF or DOCX format"}), 400

    try:
        # Extract text from file
        extracted_text = ''
        rfp_chunks = preprocess_file(rfp_file)
        extracted_text = ' '.join(rfp_chunks)

        # Convert to structured JSON using the converter
        rfp_json = json_converter.convert_to_json(extracted_text)

        # Create a filename based on the original file name
        base_filename = os.path.splitext(rfp_file.filename)[0]
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        json_filename = f"{base_filename}_{timestamp}.json"
        
        # Save to data/document_chunks directory
        chunks_dir = os.path.join(app.root_path, 'data', 'document_chunks')
        os.makedirs(chunks_dir, exist_ok=True)
        json_path = os.path.join(chunks_dir, json_filename)
        
        # Save the JSON file
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(rfp_json, f, indent=2, ensure_ascii=False)

        # Return both the JSON content and the saved file path
        return jsonify({
            "data": rfp_json,
            "saved_to": json_path
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
