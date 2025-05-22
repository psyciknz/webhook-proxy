import os
import logging
from urllib.parse import urlparse, parse_qs
from flask import Flask, request, Response
import requests

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
def webhook_proxy():
    logger.info("Start")
    
    # Get token from query parameters
    token = request.args.get('token')
    if not token:
        return Response('Token not provided', status=400)
    
    logger.info(f"Token: {token}")
    
    # Verify token against webhook secret
    webhook_secret = os.getenv('WEBHOOK_SECRET')
    if token != webhook_secret:
        return Response(
            ":(",
            status=401,
            headers={'content-type': 'text/plain'}
        )
    
    # Construct target URL
    ryot_url = os.getenv('RYOT_URL')
    target_url = f"{ryot_url}/_i/{webhook_secret}"
    logger.info(f"Target URL: {target_url}")
    
    # Prepare headers for the forwarded request
    headers = dict(request.headers)
    headers['CF-Access-Client-Id'] = os.getenv('CF_CLIENT_ID')
    headers['CF-Access-Client-Secret'] = os.getenv('CF_CLIENT_SECRET')
    
    # Remove hop-by-hop headers that shouldn't be forwarded
    hop_by_hop_headers = [
        'connection', 'keep-alive', 'proxy-authenticate',
        'proxy-authorization', 'te', 'trailers', 'transfer-encoding',
        'upgrade', 'host'
    ]
    for header in hop_by_hop_headers:
        headers.pop(header, None)
    
    logger.info(f"Forwarding request with headers: {headers}")
    
    try:
        # Forward the request
        response = requests.request(
            method=request.method,
            url=target_url,
            headers=headers,
            data=request.get_data(),
            params=request.args,
            allow_redirects=False
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
