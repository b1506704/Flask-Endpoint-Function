import azure.functions as func
import logging
import json

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.route(route="prompt_handler")
def prompt_handler(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    prompt = ''

    try:
        req_body = req.get_json()
    except ValueError:
        pass
    else:
        prompt = req_body.get('prompt')

    #logic to call OpenAPI here
    response = { "suggestion" : "This is the data generated from OpenAI."}

    if prompt:
        return func.HttpResponse(json.dumps(response))
    else:
        response = { "error" : "Cannot generate suggestions due to technical issues."}

        return func.HttpResponse(
             json.dumps(response),
             status_code=500
        )