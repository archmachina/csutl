
import sys
import subprocess
import pytest
import csutl
import json

from datetime import datetime, timedelta

class TestCli:
    def test_1(self):
        sys.argv = ["csutl", "--help"]

        with pytest.raises(SystemExit):
            res = csutl.cli.main()

    def test_2(self):
        # Test running the entrypoint
        ret = subprocess.call(["/work/bin/entrypoint", "--help"])

        assert ret == 0

    def test_public_api1(self):
        # Test access to the public api
        ret = subprocess.call(["/work/bin/entrypoint", "get", "/pubapi/v2/latest"])

        assert ret == 0

    def test_public_api2(self):
        # Test access to the public api
        ret = subprocess.call(["/work/bin/entrypoint", "get", "/pubapi/v2/latest/BTC"])

        assert ret == 0

    def test_order_history1(self):
        """
        Test that the order history subcommand is available
        """

        ret = subprocess.call(["/work/bin/entrypoint", "order_history", "--help"])

        assert ret == 0

    def test_price_history1(self):
        """
        Test that the price history subcommand is available
        """

        ret = subprocess.call(["/work/bin/entrypoint", "price_history", "--help"])

        assert ret == 0

    def test_price_history2(self):
        """
        Test that the price history can capture 1 hours worth of history
        """

        result = subprocess.run(["/work/bin/entrypoint", "price_history", "btc", "-a", "1"], stdout=subprocess.PIPE, stdin=subprocess.DEVNULL, text=True)

        assert result.returncode == 0
        response = json.loads(result.stdout)

        assert isinstance(response, list)
        assert len(response) > 0
        assert all(isinstance(x, list) for x in response)
        assert all(len(x) == 2 for x in response)
        assert all(isinstance(x[0], (int, float)) for x in response)
        assert all(isinstance(x[1], (int, float)) for x in response)

    def test_price_history3(self):
        """
        Test that the price history can capture 1 hours worth of history stats
        """

        result = subprocess.run(["/work/bin/entrypoint", "price_history", "btc", "-a", "1", "-s"], stdout=subprocess.PIPE, stdin=subprocess.DEVNULL, text=True)

        assert result.returncode == 0
        response = json.loads(result.stdout)


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

    def test_market_orders1(self):
        """
        Test that the market orders subcommand is available
        """

        ret = subprocess.call(["/work/bin/entrypoint", "market", "orders", "--help"])

        assert ret == 0

    def test_market_buy1(self):
        """
        Test that the market buy subcommand is available
        """

        ret = subprocess.call(["/work/bin/entrypoint", "market", "buy", "--help"])

        assert ret == 0

    def test_market_sell1(self):
        """
        Test that the market sell subcommand is available
        """

        ret = subprocess.call(["/work/bin/entrypoint", "market", "sell", "--help"])

        assert ret == 0

