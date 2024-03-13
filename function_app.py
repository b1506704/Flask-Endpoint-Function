import azure.functions as func
import logging
import json
from openai import OpenAI
client = OpenAI(api_key='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')

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.route(route="prompt_handler")
def prompt_handler(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    prompt = ''

    try:
        req_body = req.get_json()

    except Exception as e:
        return func.HttpResponse(
        json.dumps({"error": "Invalid request body. Please provide a valid JSON object."}),
        status_code=400
    )

    else:
        prompt = req_body.get('prompt')

    if prompt:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            max_tokens=4096,
            messages=[{"role": "system", "content": "You are a helpful assistant."},
                      {"role": "user", "content": prompt}]
        )

        return func.HttpResponse(json.dumps({"suggestion": response.choices[0].message.content}), status_code=200)
    else:
        return func.HttpResponse(
            json.dumps({"error": "An error occurred while processing the request."}),
            status_code=500
        )