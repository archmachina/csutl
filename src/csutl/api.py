
import time
import json
import hashlib
import hmac
import urllib.parse
import requests
import logging
import os

from .common import val_arg, val_run

logger = logging.getLogger(__name__)

class CoinSpotApi:
    def __init__(self, base_url=None, requestor=None):
        val_arg(isinstance(base_url, (str, type(None))), "Invalid base_url passed to CoinSpotApi")
        val_arg(requestor is None or callable(requestor), "Invalid requestor passed to CoinSpotApi")

        # Default base url
        if base_url is None:
            base_url = "https://www.coinspot.com.au"

        self.base_url = base_url

        def default_requestor(method, url, headers, payload):
            response = requests.request(method, url, headers=headers, data=payload)
            response.raise_for_status()
            return response.text

        # This can be overridden for testing
        if requestor is None:
            requestor = default_requestor

        self.requestor = requestor

    def get(self, url):

        # Process incoming arguments
        val_arg(isinstance(url, str), "Invalid url provided to CoinSpotApi.get")
        val_arg(url != "", "Empty url provided to CoinSpotApi.get")

        # Convert URL to an absolute url, if not already
        url = urllib.parse.urljoin(self.base_url, url)

        # Headers for request
        headers = self.build_headers()

        # Make request to the endpoint
        logger.debug("url: %s", url)
        logger.debug("headers: %s", headers)
        response = self.requestor("get", url, headers, payload=None)

        logger.debug("Response: %s", response)

        return response

    def post(self, url, payload, raw_payload=False):

        # Process incoming arguments
        val_arg(isinstance(url, str), "Invalid url provided to CoinSpotApi.post")
        val_arg(url != "", "Empty url provided to CoinSpotApi.post")
        val_arg(isinstance(raw_payload, bool), "Invalid raw_payload argument to CoinSpotApi.post")
        val_arg(isinstance(payload, str), "Invalid payload type passed to CoinSpotApi.post")

        # Convert URL to an absolute url, if not already
        url = urllib.parse.urljoin(self.base_url, url)

        # Parse the payload input and add the nonce, if required
        if not raw_payload:
            parsed = json.loads(payload)
            parsed["nonce"] = str(time.time_ns())
            payload = json.dumps(parsed, separators=(",", ":"))

        # Headers for request
        headers = self.build_headers(payload=payload)

        # Make request to the endpoint
        logger.debug("url: %s", url)
        logger.debug("headers: %s", headers)
        logger.debug("payload: %s", payload)
        response = self.requestor("post", url, headers, payload)

        logger.debug("Response: %s", response)

        return response

    def build_headers(self, payload=None):

        # Common headers
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        # CoinSpot differentiates between authorised endpoints and public endpoints by method
        # POST is authenticated, while GET is reserved for public endpoints
        # If there is a payload, then we'll add authentication headers

        if payload is not None:
            val_run(isinstance(payload, str), "Invalid payload type passed to build_headers")

            # Retrieve the api key and secret
            apikey = os.environ.get("COINSPOT_API_KEY", "")
            apisecret = os.environ.get("COINSPOT_API_SECRET", "")

            val_run(apikey != "", "Missing api key in COINSPOT_API_KEY")
            val_run(apisecret != "", "Missing api secret in COINSPOT_API_SECRET")

            headers["Key"] = apikey
            headers["Sign"] = hmac.new(apisecret.encode("utf-8"), payload.encode("utf-8"), hashlib.sha512).hexdigest()

        return headers


