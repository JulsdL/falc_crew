from docx import Document
import os

directory = "data/reference_models"

for file in os.listdir(directory):
    if file.endswith(".docx"):
        path = os.path.join(directory, file)
        try:
            Document(path)
            print(f"✅ Valid: {file}")
        except Exception as e:
            print(f"❌ Invalid: {file} — {e}")
