from flask import Flask, request, jsonify # type: ignore
from utils.text_cleaner import preprocess_file
from utils.embedding import generate_embeddings
from utils.vector_store import store_chunks
from agents.eligibility_agent import check_eligibility
from agents.checklist_agent import generate_checklist
from agents.risk_analysis_agent import analyze_risks

app = Flask(__name__)

@app.route('/analyze', methods=['POST'])
def analyze_rfp():
    rfp_file = request.files.get('rfp')
    company_profile = request.files.get('company_profile')

    if not rfp_file or not company_profile:
        return jsonify({"error": "Both RFP and company profile files are required"}), 400

    # Preprocess files
    rfp_text = preprocess_file(rfp_file)
    profile_text = preprocess_file(company_profile)

    # Generate embeddings and store chunks
    chunks = generate_embeddings(rfp_text)
    store_chunks(chunks)

    # Run agents
    eligibility = check_eligibility(profile_text, chunks)
    checklist = generate_checklist(chunks)
    risks = analyze_risks(chunks)

    return jsonify({
        "eligibility": eligibility,
        "checklist": checklist,
        "risks": risks
    })

if __name__ == '__main__':
    app.run(debug=True)
