from flask import Flask, request, jsonify
import pytesseract
from PIL import Image
import pdfplumber
import os

app = Flask(__name__)

def extract_text_from_pdf(file_path):
    try:
        with pdfplumber.open(file_path) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text() or ""
            return text.strip()
    except Exception as e:
        return f"[PDF Error] {str(e)}"

def extract_text_from_image(file_path):
    try:
        image = Image.open(file_path)
        text = pytesseract.image_to_string(image)
        return text.strip()
    except Exception as e:
        return f"[Image Error] {str(e)}"

@app.route("/extract-text", methods=["POST"])
def extract_text():
    data = request.get_json()
    if not data or "file_url" not in data:
        return jsonify({"error": "Missing 'file_url' in request body"}), 400

    file_url = data["file_url"]
    filename = "temp_input_file"

    try:
        import requests
        response = requests.get(file_url)
        if response.status_code != 200:
            return jsonify({"error": "Could not download file"}), 400

        content_type = response.headers.get("Content-Type", "")
        if "pdf" in content_type:
            filename += ".pdf"
        elif "image" in content_type or "jpeg" in content_type or "jpg" in content_type or "png" in content_type:
            filename += ".jpg"
        else:
            return jsonify({"error": "Unsupported file type"}), 400

        with open(filename, "wb") as f:
            f.write(response.content)

        if filename.endswith(".pdf"):
            extracted_text = extract_text_from_pdf(filename)
        else:
            extracted_text = extract_text_from_image(filename)

        os.remove(filename)
        return jsonify({"text": extracted_text})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ✅ PORT ayarı Render için zorunludur
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
