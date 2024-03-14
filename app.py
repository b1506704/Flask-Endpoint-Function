import os
from flask import (Flask, jsonify, request, render_template, send_from_directory)

app = Flask(__name__)

@app.route('/')
def index():
   print('Request for index page received')
   return render_template('index.html')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/api/prompt_handler', methods=['POST'])
def handle_prompt():
    try:
        req_body = request.get_json()

    except Exception as e:
        return jsonify({"error": "Invalid request body. Please provide a valid JSON object."}), 400
        
    else:
        prompt = req_body.get('prompt')

        if prompt:
            from openai import OpenAI
            client = OpenAI(api_key = os.environ["OPENAI_API_KEY"])
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                max_tokens=4096,
                messages=[{"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": prompt}]
            )

            return jsonify({"suggestion": response.choices[0].message.content})
        else:
            return jsonify({"error": "Invalid request body. Please provide a valid JSON object."}), 500

if __name__ == '__main__':
   app.run()
