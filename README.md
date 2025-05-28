# Plex Webhook Proxy

Plex Webhook Proxy is a simple proxy service to taking Plex Webhooks externally from your network and sending them to consuming services internally.  

When a plex webhook is internal to your network only, only your local server can interact with the services.  
By hosting it on the WAN side of your network, it can scrobble events from servers onther than your own.

## Setup

### Environment Variables
Copy Sample.env file as .env and update the secret and RYOT_URL to an existing Webhook url as specified by a consumeing service.
```
LOGLEVEL=DEBUG
WEBHOOK_SECRET=<secret that can be used to authenticate you webhook>
RYOT_URL=<Full url for service consuming the webhook, eg yamtrack/ryot/mediatracker>
```

