from transformers import pipeline

qa_pipeline = pipeline("question-answering", model="bert-large-uncased-whole-word-masking-finetuned-squad")

def explain_jargon(text):
    try:
        result = qa_pipeline(question="What does this term mean?", context=text)
        return result['answer'] if result['score'] > 0.5 else "Could not find explanation."
    except Exception:
        return "Could not find explanation."
