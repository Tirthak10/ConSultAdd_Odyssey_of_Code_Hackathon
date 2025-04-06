import os

# Base project directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ChromaDB settings
CHROMA_SETTINGS = {
    "persist_directory": os.path.join(BASE_DIR, "chroma_db"),
    "anonymized_telemetry": False
}
