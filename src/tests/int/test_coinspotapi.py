
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

    def test_validate_status1(self):
        """
        Use the public api to check validation of status
        """

        api = csutl.CoinSpotApi()
        api.get("/pubapi/v2/latest")
        # Should validate the status and message fields, checking for ok

    def test_validate_status2(self):
        """
        Check validation for an ok status and message response
        """

        def test_requestor(method, url, headers, payload=None):
            return json.dumps({"status": "ok", "message": "ok"})

        api = csutl.CoinSpotApi(requestor=test_requestor)
        api.get("/pubapi/v2/latest")

    def test_validate_status3(self):
        """
        Provide a failed status, but ok message
        """

        def test_requestor(method, url, headers, payload=None):
            return json.dumps({"status": "bad", "message": "ok"})

        api = csutl.CoinSpotApi(requestor=test_requestor)
        with pytest.raises(csutl.exception.RuntimeException):
            api.get("/pubapi/v2/latest")

    def test_validate_status4(self):
        """
        Provide a failed message, but ok status
        """

        def test_requestor(method, url, headers, payload=None):
            return json.dumps({"status": "ok", "message": "bad"})

        api = csutl.CoinSpotApi(requestor=test_requestor)
        with pytest.raises(csutl.exception.RuntimeException):
            api.get("/pubapi/v2/latest")

    def test_validate_status5(self):
        """
        Provide a failed message and failed status
        """

        def test_requestor(method, url, headers, payload=None):
            return json.dumps({"status": "bad", "message": "bad"})

        api = csutl.CoinSpotApi(requestor=test_requestor)
        with pytest.raises(csutl.exception.RuntimeException):
            api.get("/pubapi/v2/latest")

    def test_post_obj1(self):
        """
        Test post for a string object.
        Post should support both strings and other objects
        """

        def test_requestor(method, url, headers, payload=None):
            content = json.loads(payload)

            assert "test" in content
            assert content["test"] == "other"

            return "{}"

        os.environ["COINSPOT_API_KEY"] = "apikey"
        os.environ["COINSPOT_API_SECRET"] = "apisecret"

        api = csutl.CoinSpotApi(requestor=test_requestor)
        api.post("/nowhere", "{\"test\":\"other\"}")

    def test_post_obj1(self):
        """
        Test post for a custom object
        Post should support both strings and other objects
        """

        def test_requestor(method, url, headers, payload=None):
            content = json.loads(payload)

            assert "test" in content
            assert content["test"] == "other"

            return "{}"

        os.environ["COINSPOT_API_KEY"] = "apikey"
        os.environ["COINSPOT_API_SECRET"] = "apisecret"

        api = csutl.CoinSpotApi(requestor=test_requestor)
        api.post("/nowhere", {"test":"other"})

    def test_prune_status1(self):
        """
        Test pruning of status messages
        """

        def test_requestor(method, url, headers, payload=None):
            return json.dumps({"status": "ok", "message": "ok", "test": "response"})

        api = csutl.CoinSpotApi(requestor=test_requestor)
        response = json.loads(api.get("/pubapi/v2/latest"))

        assert "status" not in response
        assert "message" not in response
        assert "test" in response and response["test"] == "response"

    def test_prune_status2(self):
        """
        Test status messages in raw response
        """

        def test_requestor(method, url, headers, payload=None):
            return json.dumps({"status": "ok", "message": "ok", "test": "response"})

        api = csutl.CoinSpotApi(requestor=test_requestor)
        response = json.loads(api.get("/pubapi/v2/latest", raw_output=True))

        assert "status" in response and response["status"] == "ok"
        assert "message" in response and response["message"] == "ok"
        assert "test" in response and response["test"] == "response"

