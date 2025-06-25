
import sys
import subprocess
import pytest
import csutl

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

