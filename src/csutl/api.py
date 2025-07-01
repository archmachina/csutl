
import time
import json
import hashlib
import hmac
import urllib.parse
import requests
import logging
import os
import statistics
import math

from datetime import datetime, timedelta

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

    def get(self, url, raw_output=False):

        # Process incoming arguments
        val_arg(isinstance(url, str), "Invalid url provided to CoinSpotApi.get")
        val_arg(url != "", "Empty url provided to CoinSpotApi.get")
        val_arg(isinstance(raw_output, bool), "Invalid raw_output value supplied to CoinSpotApi.get")

        # Convert URL to an absolute url, if not already
        url = urllib.parse.urljoin(self.base_url, url)

        # Headers for request
        headers = self.build_headers()

        # Make request to the endpoint
        logger.debug("url: %s", url)
        logger.debug("headers: %s", headers)
        response = self.requestor("get", url, headers, payload=None)

        logger.debug("Response: %s", response)

        if not raw_output:
            response = self.process_response(response)

        return response

    def post(self, url, payload, raw_payload=False, raw_output=False):

        # Process incoming arguments
        val_arg(isinstance(url, str), "Invalid url provided to CoinSpotApi.post")
        val_arg(url != "", "Empty url provided to CoinSpotApi.post")
        val_arg(isinstance(raw_payload, bool), "Invalid raw_payload argument to CoinSpotApi.post")
        val_arg(isinstance(raw_output, bool), "Invalid raw_output value supplied to CoinSpotApi.post")

        # Convert payload, if required
        if not isinstance(payload, str):
            payload = json.dumps(payload)

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

        if not raw_output:
            response = self.process_response(response)

        return response

    def process_response(self, response):

        # Validate incoming args
        val_arg(isinstance(response, str), "Invalid type for response")

        # Deserialise response
        content = json.loads(response)

        # Check for status messages
        if "status" in content:
            val_run(content["status"] == "ok", "API did not return 'ok' for status")
            content.pop("status")

        if "message" in content:
            val_run(content["message"] == "ok", "API did not return 'ok' for message")
            content.pop("message")

        # Return the new version of the response
        return json.dumps(content)

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

    def get_price_history(self, coin, age_hours=7, stats=False):
        """
        Retrieve the coin price for the last x hours
        """

        # Validate incoming parameters
        val_arg(isinstance(age_hours, int) and age_hours > 0, "Invalid age_hours specified")

        # Calculate range
        now = datetime.now()
        end_date = now
        start_date = (now - timedelta(hours=age_hours))

        # Call get_price_history_range to make the request
        return self.get_price_history_range(coin, start_date, end_date, stats=stats)

    def get_price_history_range(self, coin, start_date, end_date, stats=False):
        """
        Retrieve the coin price for the specified range
        """

        # Process incoming arguments
        val_arg(isinstance(coin, str) and coin != "", "Invalid coin type passed to get_history")
        val_arg(isinstance(start_date, datetime), "Invalid start_date passed to get_price_history_range")
        val_arg(isinstance(end_date, datetime), "Invalid end_date passed to get_price_history_range")

        # Calculate start and end times
        start = int(start_date.timestamp() * 1000)
        end = int(end_date.timestamp() * 1000)

        # Coinspot only recognises upper case coin types
        coin = coin.upper()

        # Build the query url
        url = urllib.parse.urljoin(self.base_url, f"/charts/history_basic?symbol={coin}&from={start}&to={end}")

        # Headers for request
        headers = self.build_headers()

        # Make request to the endpoint
        logger.debug("url: %s", url)
        logger.debug("headers: %s", headers)
        response = self.requestor("get", url, headers, payload=None)

        logger.debug("Response: %s", response)

        if stats:
            parsed = json.loads(response)

            val_run(isinstance(parsed, list), "Invalid response from endpoint - not a list")
            val_run(all(isinstance(x, list) for x in parsed), "Invalid response from endpoint - Some items are not lists")
            val_run(all(len(x) == 2 for x in parsed), "Invalid response from endpoint - Elements should have two items")
            val_run(len(parsed) > 0, "Invalid response from endpoint - Empty array")

            prices = [x[1] for x in parsed]
            val_run(all(not math.isnan(x) for x in prices), "Invalid response from endpoint - NaN values")

            price_first = prices[0]
            price_last = prices[-1]

            price_min = min(prices)
            price_max = max(prices)

            quartiles = statistics.quantiles(prices)
            quartile_index = sum(1 for x in quartiles if price_last > x)

            width = price_max - price_min
            width_index = (price_last - price_min) / width

            median = statistics.median(prices)
            pstdev = statistics.pstdev(prices)
            pstdev_index = (price_last - median) / pstdev

            stats_response = {
                "start_date": start_date.astimezone().isoformat(),
                "end_date": end_date.astimezone().isoformat(),
                "coin": coin,
                "first": price_first,
                "last": price_last,
                "min": price_min,
                "max": price_max,
                "avg": statistics.mean(prices),
                "med": median,
                "width": width,
                "growth": price_last - price_min,
                "quartiles": quartiles,
                "pstdev": statistics.pstdev(prices),
                "latest": {
                    "quartile_index": quartile_index,
                    "width_index": width_index,
                    "pstdev_index": pstdev_index
                }
            }

            response = json.dumps(stats_response)

        return response

