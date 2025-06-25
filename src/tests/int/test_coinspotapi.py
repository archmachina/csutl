
import sys
import subprocess
import pytest
import csutl
import json
import os

class TestCoinSpotApi:
    def test_public_api1(self):
        """
        Test access to the public API
        """

        api = csutl.CoinSpotApi()
        response = api.get("/pubapi/v2/latest")

        assert response is not None
        assert isinstance(response, str)

        parsed = json.loads(response)

        # status
        assert "status" in parsed
        status = parsed["status"]
        
        assert isinstance(status, str) and status == "ok"

        # prices
        assert "prices" in parsed
        prices = parsed["prices"]

        assert isinstance(prices, dict)

    def test_public_api2(self):
        """
        Test access to the public API
        """

        api = csutl.CoinSpotApi()
        response = api.get("/pubapi/v2/latest/BTC")

        assert response is not None
        assert isinstance(response, str)

        parsed = json.loads(response)

        # status
        assert "status" in parsed
        status = parsed["status"]
        
        assert isinstance(status, str) and status == "ok"

        # prices
        assert "prices" in parsed
        prices = parsed["prices"]

        assert isinstance(prices, dict)

    def test_nonce1(self):
        """
        Test insertion of the nonce in the the payload
        """

        def test_requestor(method, url, headers, payload=None):
            assert isinstance(payload, str)
            parsed = json.loads(payload)

            assert "nonce" in parsed
            assert isinstance(parsed["nonce"], str)
            assert int(parsed["nonce"]) > 0

            return "{}"

        os.environ["COINSPOT_API_KEY"] = "apikey"
        os.environ["COINSPOT_API_SECRET"] = "apisecret"

        api = csutl.CoinSpotApi(requestor=test_requestor)

        response = api.post("/pubapi/v2/status", "{}")

    def test_nonce2(self):
        """
        Test insertion of ascending nonces in consequetive requests
        """

        class ReqTest:
            def __init__(self):
                self.last = 0

            def test_requestor(self, method, url, headers, payload=None):
                assert isinstance(payload, str)
                parsed = json.loads(payload)

                assert "nonce" in parsed
                assert isinstance(parsed["nonce"], str)
                nonce = int(parsed["nonce"])

                assert nonce > self.last
                self.last = nonce

                return "{}"

        os.environ["COINSPOT_API_KEY"] = "apikey"
        os.environ["COINSPOT_API_SECRET"] = "apisecret"

        req = ReqTest()
        api = csutl.CoinSpotApi(requestor=req.test_requestor)

        # Make two requests
        response = api.post("/pubapi/v2/status", "{}")
        assert isinstance(response, str) and response == "{}"

        response = api.post("/pubapi/v2/status", "{}")
        assert isinstance(response, str) and response == "{}"

    def test_auth1(self):
        """
        Ensure no auth is provided on get requests
        """

        def test_requestor(method, url, headers, payload=None):
            assert isinstance(headers, dict)
            assert "Key" not in headers
            assert "Sign" not in headers

            return "{}"

        api = csutl.CoinSpotApi(requestor=test_requestor)

        response = api.get("/pubapi/v2/latest")
        assert isinstance(response, str) and response == "{}"

    def test_auth2(self):
        """
        Ensure auth is provided on post requests
        """

        def test_requestor(method, url, headers, payload=None):
            assert isinstance(headers, dict)
            assert "Key" in headers
            assert headers["Key"] == "apikey"

            assert "Sign" in headers

            return "{}"

        api = csutl.CoinSpotApi(requestor=test_requestor)

        os.environ["COINSPOT_API_KEY"] = "apikey"
        os.environ["COINSPOT_API_SECRET"] = "apisecret"

        response = api.post("/pubapi/v2/status", "{}")
        assert isinstance(response, str) and response == "{}"

    def test_auth3(self):
        """
        Check failure on missing api key
        """

        def test_requestor(method, url, headers, payload=None):
            return "{}"

        api = csutl.CoinSpotApi(requestor=test_requestor)

        os.environ.pop("COINSPOT_API_KEY", "")
        os.environ["COINSPOT_API_SECRET"] = "apisecret"

        with pytest.raises(csutl.exception.RuntimeException):
            response = api.post("/pubapi/v2/status", "{}")

    def test_auth4(self):
        """
        Check failure on missing api key
        """

        def test_requestor(method, url, headers, payload=None):
            return "{}"

        api = csutl.CoinSpotApi(requestor=test_requestor)

        os.environ["COINSPOT_API_KEY"] = "apikey"
        os.environ.pop("COINSPOT_API_SECRET", "")

        with pytest.raises(csutl.exception.RuntimeException):
            response = api.post("/pubapi/v2/status", "{}")

