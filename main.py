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
    service_url_string = os.getenv('SERVICE_URLS')
    service_urls: list
    service_urls = service_url_string.split(",")
    
    logger.info("Start")
    if request.method == 'GET':
        logger.info(f"WebHook Secret: {webhook_secret}")
        logger.info(f"URL: {','.join(service_urls)}")
        return Response(f"WebHook Secret: {webhook_secret}",200)
        
        
    
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
    logger.info(f"Target URL: {','.join(service_urls)}")
    try:
        logger.debug(data)
    except:
        pass
    
    # Prepare headers for the forwarded request
    headers = dict(request.headers)
    if 'User-Agent' in headers:
        headers['User-Agent'] = f'Webhook-proxy {version}'

    logger.debug(headers)
    for url in service_urls:
        try:
            # Forward the request
            response = requests.request(
                method=request.method,
                headers=headers,
                url=url,
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
            
            if response.status_code > 400:
                returnerror = response.status_code
                returncontent = response.content
            
            returnheaders = response_headers
            
        except requests.RequestException as e:
            logger.error(f"Request failed: {e}")
            returnerror =500
            returncontent = f'Internal Server Error: {e}'
            
    
    #for url in service_urls:
    if returnerror is not None:
        return Response(
                    returncontent,
                    status=returnerror,
                    headers=returnheaders
                )
    else:
        return Response(
                    "success",
                    status=200,
                    headers=returnheaders
                )
#def webhook_proxy():
    
if __name__ == '__main__':
    port = int(os.getenv('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
