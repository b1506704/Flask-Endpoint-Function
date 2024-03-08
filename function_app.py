import azure.functions as func
import logging
import json
import os
from openai import OpenAI
client = OpenAI(api_key='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')

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.route(route="prompt_handler")
def prompt_handler(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    prompt = ''

    try:
        prompt = "Hello, How are you today?"

        if prompt:
            response = client.chat.completions.create(
                        model="gpt-3.5-turbo",  
                        max_tokens=4096,  
                        messages=[{"role": "system", "content": "You are a helpful assistant."},
                                {"role": "user", "content": prompt}]
            )

            print(response.choices[0].message.content)
 
            return func.HttpResponse(json.dumps({"suggestion": response.choices[0].message.content}), status_code=200)
        else:
            return func.HttpResponse(
                json.dumps({"error": "Please provide a prompt in the request body."}),
                status_code=400
            )
    except Exception as e:
        logging.exception(f"Error calling OpenAI API: {e}")
        return func.HttpResponse(
            json.dumps({"error": "An error occurred while processing the request."}),
            status_code=500
        )