import os
import logging
import json
from urllib.parse import urlparse, parse_qs
from flask import Flask, request, Response
import requests
from dotenv import load_dotenv,dotenv_values

load_dotenv(".env")

version = "0.1"

LOGLEVEL = os.getenv('LOGLEVEL','INFO').upper()
print(LOGLEVEL)
# Configure logging
logging.basicConfig(level=LOGLEVEL)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route('/', methods=['GET','POST'])
def webhook_proxy():
    load_dotenv(".env")
    webhook_secret = os.getenv('WEBHOOK_SECRET')
    ryot_url = os.getenv('RYOT_URL')
    logger.info("Start")
    if request.method == 'GET':
        logger.info(f"WebHook Secret: {webhook_secret}")
        logger.info(f"URL: {ryot_url}")
        return Response(f"WebHook Secret: {webhook_secret}, URL:{ryot_url}",200)
        
        
    
    # Get token from query parameters
    token = request.args.get('token')
    if not token:
        return Response('Token not provided', status=400)
    
    logger.info(f"Token: {token}")
    
    # Verify token against webhook secret
    logger.debug(f"Webhook secret {webhook_secret} to compare to token {token}")
    if token != webhook_secret:
        return Response(
            ":(",
            status=401,
            headers={'content-type': 'text/plain'}
        )
    #data = str(request.get_data())
    data = request.get_data()
    try:
        logger.info("Loading data to json object")
        datajson = json.loads(request.form['payload'])
        logger.info(f"Event: {datajson['event']}")
        logger.info(f"Server: {datajson['Server']['title']}")
    except:
        pass
    # Remove all Unicode characters from the value

    #data= data.replace("\\x", "")    
    # Construct target URL
    #target_url = f"{ryot_url}/_i/{webhook_secret}"
    logger.info(f"Target URL: {ryot_url}")
    try:
        logger.debug(data)
    except:
        pass
    
    # Prepare headers for the forwarded request
    headers = dict(request.headers)
    if 'User-Agent' in headers:
        headers['User-Agent'] = f'Webhook-proxy {version}'

    logger.debug(headers)
    try:
        # Forward the request
        response = requests.request(
            method=request.method,
            headers=headers,
            url=ryot_url,
            data=data,
            allow_redirects=True
        )
        
        logger.info(f"Response status: {response.status_code}")
        
        # Create response with same status and headers
        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        response_headers = [
            (name, value) for name, value in response.headers.items()
            if name.lower() not in excluded_headers
        ]
        
        return Response(
            response.content,
            status=response.status_code,
            headers=response_headers
        )
        
    except requests.RequestException as e:
        logger.error(f"Request failed: {e}")
        return Response('Internal Server Error', status=500)

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
