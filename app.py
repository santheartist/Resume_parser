import os
import sys
from flask import Flask, request, render_template
from pypdf import PdfReader
from resumeparser import ats_extractor

sys.path.insert(0, os.path.abspath(os.getcwd()))

UPLOAD_PATH = os.path.join(os.getcwd(), "uploads")
if not os.path.exists(UPLOAD_PATH):
    os.makedirs(UPLOAD_PATH)

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route("/process", methods=["POST"])
def ats():
    doc = request.files['pdf_doc']
    target_role = request.form.get("target_role", "")
    doc_path = os.path.join(UPLOAD_PATH, "file.pdf")
    doc.save(doc_path)

    resume_text = _read_file_from_path(doc_path)
    extracted_data = ats_extractor(resume_text, target_role)

    return render_template('index.html', data=extracted_data)

def _read_file_from_path(path):
    reader = PdfReader(path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)

