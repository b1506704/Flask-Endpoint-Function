import os
from flask import (Flask, jsonify, redirect, request,
                   render_template, send_from_directory, url_for)
import PyPDF2
from werkzeug.utils import secure_filename

app = Flask(__name__)

ALLOWED_EXTENSIONS = {'txt', 'pdf'}


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# format the response
def format_response(text):
    
    lines = []
    for line in text.splitlines():

        formatted_line = (line.strip()).replace("*", "").replace("#", "")
        lines.append(formatted_line)

    return lines
# end format the response

@app.route('/')
def index():
    print('Request for index page received')
    return render_template('index.html')


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route('/hello', methods=['POST'])
def hello():
    name = request.form.get('name')

    if name:
        print('Request for hello page received with name=%s' % name)
        return render_template('hello.html', name=name)
    else:
        print('Request for hello page received with no name or blank name -- redirecting')
        return redirect(url_for('index'))


@app.route('/api/prompt_handler', methods=['POST'])
def handle_prompt():
    try:
        req_body = request.get_json()

    except Exception as e:
        return jsonify({"error": "Invalid request body. Please provide a valid JSON object."}), 400

    else:
        prompt = req_body.get('prompt')

        if prompt:
            import openai
            openai.api_key = os.environ["OPENAI_API_KEY"]
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                max_tokens=4096,
                messages=[{"role": "system", "content": "You are a helpful assistant."},
                          {"role": "user", "content": prompt}]
            )

            return jsonify({"suggestion": format_response(response.choices[0].message.content)})
        else:
            return jsonify({"error": "Invalid request body. Please provide a valid JSON object."}), 500


@app.route('/api/upload-file', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'message': 'No file uploaded'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'message': 'No selected file'}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        PATH = 'uploads/document'
        file_path = os.path.join(PATH, filename)
        file.save(file_path)

        text_content = extract_text(file_path)

        if (text_content):
            import openai
            openai.api_key = os.environ["OPENAI_API_KEY"]
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                max_tokens=4096,
                messages=[{"role": "system", "content": "You are a helpful assistant."},
                          {"role": "user", "content": text_content}]
            )

            return jsonify({"suggestion": format_response(response.choices[0].message.content)})

        return jsonify({'message': 'File uploaded successfully!', 'text_content': text_content}), 201
    else:
        return jsonify({'message': 'Please upload allowed file types: txt, pdf'}), 415


def extract_text(file_path):
    if os.path.splitext(file_path)[1].lower() == '.txt':
        with open(file_path, 'r') as f:
            return f.read()
    elif os.path.splitext(file_path)[1].lower() == '.pdf':
        with open(file_path, 'rb') as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            num_pages = len(pdf_reader.pages)
            text = ''
            for page_num in range(num_pages):
                page = pdf_reader.pages[page_num]
                text += page.extract_text()
            return text
    else:
        return jsonify({'message': 'Unsupported file type'}), 415


if __name__ == '__main__':
    app.run()
