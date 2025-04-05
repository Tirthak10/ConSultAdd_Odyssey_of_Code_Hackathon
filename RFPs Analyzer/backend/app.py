from flask import Flask, request, jsonify # type: ignore

app = Flask(__name__)

@app.route('/upload', methods=['POST'])
def upload_files():
    # Placeholder for handling uploaded files
    rfp_file = request.files.get('rfp')
    company_profile = request.files.get('company_profile')
    if not rfp_file or not company_profile:
        return jsonify({"error": "Both RFP and company profile files are required"}), 400
    # Process files (e.g., save to disk, preprocess, etc.)
    return jsonify({"message": "Files uploaded successfully"}), 200

if __name__ == '__main__':
    app.run(debug=True)
