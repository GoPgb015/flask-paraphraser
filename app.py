from flask import Flask, request, render_template, jsonify
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import language_tool_python
import PyPDF2
import os

app = Flask(__name__)

# Load Parrot Paraphraser model and tokenizer (loaded once at startup)
tokenizer = AutoTokenizer.from_pretrained("prithivida/parrot_paraphraser_on_T5")
model = AutoModelForSeq2SeqLM.from_pretrained("prithivida/parrot_paraphraser_on_T5")
grammar_tool = language_tool_python.LanguageTool('en-US')

# Function to paraphrase based on style
def paraphrase(text, style="Simple"):
    inputs = tokenizer(text, return_tensors="pt", padding=True, max_length=512, truncation=True)
    
    if style == "Simple":
        outputs = model.generate(**inputs, do_sample=True, top_k=50, top_p=0.95)
    elif style == "Grammar Correction":
        corrected_text = grammar_tool.correct(text)
        inputs = tokenizer(corrected_text, return_tensors="pt", padding=True, max_length=512, truncation=True)
        outputs = model.generate(**inputs, do_sample=True, top_k=50, top_p=0.95)
    elif style == "Academic Style":
        outputs = model.generate(**inputs, do_sample=True, top_k=30, top_p=0.9, temperature=0.7)
    elif style == "Creative":
        outputs = model.generate(**inputs, do_sample=True, top_k=100, top_p=0.95, temperature=1.2)
    elif style == "Special":
        outputs = model.generate(**inputs, do_sample=True, top_k=70, top_p=0.9, temperature=1.0)
    
    paraphrase_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    if style == "Academic Style":
        paraphrase_text = f"In accordance with the findings, {paraphrase_text[0].lower() + paraphrase_text[1:]}"
    elif style == "Special":
        paraphrase_text = f"Remarkably, {paraphrase_text} – a curious spin indeed!"
    return paraphrase_text

# Home route
@app.route('/')
def home():
    return render_template('index.html')

# Paraphrase route
@app.route('/paraphrase', methods=['POST'])
def paraphrase_text():
    text = ""
    style = request.form.get('style', 'Simple')
    
    # Handle PDF upload
    if 'pdf_file' in request.files:
        file = request.files['pdf_file']
        if file and file.filename.endswith('.pdf'):
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text() or ""
            text = text.strip()
    
    # Handle manual text input
    elif 'text' in request.form:
        text = request.form['text'].strip()
    
    if not text:
        return jsonify({'error': 'No text provided'}), 400
    
    paraphrased_text = paraphrase(text, style)
    return jsonify({'original': text, 'paraphrased': paraphrased_text, 'style': style})

if __name__ == '__main__':
    app.run(debug=True)