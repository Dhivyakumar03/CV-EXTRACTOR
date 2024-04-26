from flask import Flask, render_template, request, redirect, url_for
import os
import re
import pandas as pd
import fitz  

app = Flask(__name__)


UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


OUTPUT_FOLDER = os.path.join(os.getcwd(), 'output')
if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)

def extract_info_from_pdf(pdf_path):
    
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    phone_pattern = r'(\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4})'

    text = ""
    emails = set()
    phones = set()

    with fitz.open(pdf_path) as doc:
        for page in doc:
            text += page.get_text()

    emails.update(re.findall(email_pattern, text))
    phones.update(re.findall(phone_pattern, text))

    return {
        "Email": ", ".join(emails),
        "Contact No": ", ".join(phones),
        "Text": text
    }

@app.route("/", methods=["GET", "POST"])
def index():
    extracted_info = None
    if request.method == "POST":
       
        if "file" not in request.files:
            return redirect(request.url)

        file = request.files["file"]

         
        if file.filename == "":
            return redirect(request.url)

        if file:
           
            filename = file.filename
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(file_path)

            
            extracted_info = extract_info_from_pdf(file_path)

            
            os.remove(file_path)

            
            df = pd.DataFrame([extracted_info])

           
            output_file_path = os.path.join(OUTPUT_FOLDER, 'cv_data.xlsx')
            df.to_excel(output_file_path, index=False)

    return render_template("index.html", extracted_info=extracted_info)

if __name__ == "__main__":
    app.run(debug=True)




