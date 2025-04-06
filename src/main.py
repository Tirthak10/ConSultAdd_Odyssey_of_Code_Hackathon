from document_reader import read_pdf
from text_processor import preprocess_text, chunk_text
from summarizer import summarize_text
from jargon_explainer import explain_jargon
from rag_engine import RAGEngine
from eligibility_checker import extract_company_data, check_eligibility
import os

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, 'data')
    
    company_data_path = os.path.join(data_dir, 'Company Data.docx.pdf')
    rfp_path = os.path.join(data_dir, 'ELIGIBLE RFP - 1.pdf')

    # Check if data directory exists
    if not os.path.exists(data_dir):
        print(f"❌ Data directory not found at: {data_dir}")
        return

    # Check individual files
    if not os.path.exists(company_data_path):
        print(f"❌ Company data file not found at: {company_data_path}")
        return
    if not os.path.exists(rfp_path):
        print(f"❌ RFP file not found at: {rfp_path}")
        return

    company_data_text = read_pdf(company_data_path)
    rfp_text = read_pdf(rfp_path)

    if not company_data_text:
        print(f"❌ Could not read company data file: {company_data_path}")
        return
    if not rfp_text:
        print(f"❌ Could not read RFP file: {rfp_path}")
        return

    company_data = extract_company_data(company_data_text)
    preprocessed_text = preprocess_text(rfp_text)
    chunks = chunk_text(preprocessed_text)

    rag = RAGEngine()
    rag.add_documents(chunks)

    print("\n--- RFP SUMMARY ---")
    summaries = [summarize_text(chunk) for chunk in chunks]
    print(" ".join(summaries))

    print("\n--- ELIGIBILITY CHECK ---")
    status = check_eligibility(company_data, rfp_text)
    for k, v in status.items():
        print(f"{k}: {'✅' if v is True else '❌' if v is False else v}")

    if not all(v is True for v in status.values() if isinstance(v, bool)):
        print("\n--- SUGGESTIONS ---")
        for k, v in status.items():
            if v is False:
                context = rag.get_relevant_context(k)
                print(f"For '{k}': {context[:300]}...")

    while True:
        user_q = input("\nAsk a question about the RFP (or type 'exit'): ")
        if user_q.lower() == "exit":
            break
        answer = rag.query(user_q)
        print(f"\nAnswer: {answer}")

        # Jargon help
        for word in user_q.split():
            expl = explain_jargon(word)
            if "could not" not in expl.lower():
                print(f"Jargon explanation for '{word}': {expl}")
                break

if __name__ == "__main__":
    main()
