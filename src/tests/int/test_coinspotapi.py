
import sys
import subprocess
import pytest
import csutl
import json
import os

from datetime import datetime, timedelta

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

    def test_price_history1(self):
        """
        Test access to public pricing history api
        """

        api = csutl.CoinSpotApi()
        response = json.loads(api.get_price_history("BTC", age_hours=1))

        assert isinstance(response, list)
        assert len(response) > 0
        assert all(isinstance(x, list) for x in response)
        assert all(len(x) == 2 for x in response)
        assert all(isinstance(x[0], (int, float)) for x in response)
        assert all(isinstance(x[1], (int, float)) for x in response)

    def test_price_history2(self):
        """
        Test access to public pricing history api and stat generation
        """

        api = csutl.CoinSpotApi()
        response = json.loads(api.get_price_history("BTC", age_hours=1, stats=True))

        start_date = datetime.fromisoformat(response["start_date"])
        end_date = datetime.fromisoformat(response["end_date"])

        assert start_date > (datetime.now().astimezone() - timedelta(hours=2))
        assert end_date > (datetime.now().astimezone() - timedelta(hours=1))

        assert "coin" in response and response["coin"] == "BTC"
        assert "min" in response and isinstance(response["min"], (int, float))
        assert "max" in response and isinstance(response["max"], (int, float))
        assert "avg" in response and isinstance(response["avg"], (int, float))
        assert "med" in response and isinstance(response["med"], (int, float))
        assert "width" in response and isinstance(response["width"], (int, float))
        assert "growth" in response and isinstance(response["growth"], (int, float))
        assert "growth_pct" in response and isinstance(response["growth_pct"], (int, float))

        assert "quartiles" in response and isinstance(response["quartiles"], list)
        assert len(response["quartiles"]) == 3
        assert all(isinstance(x, (float, int)) for x in response["quartiles"])

        assert "ten_quantiles" in response and isinstance(response["ten_quantiles"], list)
        assert len(response["ten_quantiles"]) == 9
        assert all(isinstance(x, (float, int)) for x in response["ten_quantiles"])

        assert "pstdev" in response and isinstance(response["pstdev"], (int, float))
        assert "latest" in response and isinstance(response["latest"], dict)

        assert "quartile_index" in response["latest"]
        assert isinstance(response["latest"]["quartile_index"], (int, float))

        assert "ten_quantile_index" in response["latest"]
        assert isinstance(response["latest"]["ten_quantile_index"], (int, float))

        assert "width_index" in response["latest"]
        assert isinstance(response["latest"]["width_index"], (int, float))

        assert "pstdev_index" in response["latest"]
        assert isinstance(response["latest"]["pstdev_index"], (int, float))

