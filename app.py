from flask import Flask, request, jsonify
import pytesseract
from PIL import Image
import pdfplumber
from fpdf import FPDF
import base64
import os
import requests

app = Flask(__name__)

# 📘 PDF içinden metin çıkarma
def extract_text_from_pdf(file_path):
    try:
        with pdfplumber.open(file_path) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text() or ""
            return text.strip()
    except Exception as e:
        return f"[PDF Error] {str(e)}"

# 🖼️ Görsel içinden metin çıkarma
def extract_text_from_image(file_path):
    try:
        image = Image.open(file_path)
        text = pytesseract.image_to_string(image)
        return text.strip()
    except Exception as e:
        return f"[Image Error] {str(e)}"

# 📤 1) FlutterFlow’dan gelen dosyadan metin çıkar
@app.route("/extract-text", methods=["POST"])
def extract_text():
    data = request.get_json()
    if not data or "file_url" not in data:
        return jsonify({"error": "Missing 'file_url' in request body"}), 400

    file_url = data["file_url"]
    filename = "temp_input_file"

    try:
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

# 📄 2) FlutterFlow’dan gelen eğitim verileriyle PDF üret
@app.route("/generate_pdf", methods=["POST"])
def generate_pdf():
    try:
        data = request.get_json(force=True)

        pdf = FPDF()
        pdf.add_page()
        pdf.add_font('DejaVu', '', 'fonts/DejaVuSans.ttf', uni=True)
        pdf.set_font("DejaVu", size=12)

        pdf.cell(200, 10, txt="Training Certificate", ln=True, align='C')
        pdf.ln(10)
        pdf.cell(200, 10, txt=f"Participant: {data['traineeName']}", ln=True)
        pdf.cell(200, 10, txt=f"Company: {data['companyName']}", ln=True)
        pdf.cell(200, 10, txt=f"Type: {data['certificateType']}", ln=True)
        pdf.cell(200, 10, txt=f"Start Date: {data['startDate']}", ln=True)
        pdf.cell(200, 10, txt=f"End Date: {data['endDate']}", ln=True)
        pdf.cell(200, 10, txt=f"Duration: {data['trainingDuration']} hours", ln=True)
        pdf.cell(200, 10, txt=f"Instructor: {data['instructorName']}", ln=True)

        pdf_bytes = pdf.output(dest='S').encode('latin1')
        base64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')

        return jsonify({'pdf_base64': base64_pdf})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 🚀 Render için gerekli port ayarı
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
