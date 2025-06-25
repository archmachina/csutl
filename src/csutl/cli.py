
import argparse
import logging
import sys
import json

from .common import val_arg, val_run
from .api import CoinSpotApi

logger = logging.getLogger(__name__)

debug = False

def process_get(args):
    val_arg(isinstance(args.url, str), "Invalid type for URL")
    val_arg(args.url != "", "Empty URL provided")

    # Api for coinspot access
    api = CoinSpotApi()

    # Make request against the API
    response = api.get(args.url)

    # Display output from the API, formatting if required
    if args.raw_output:
        print(response)
    else:
        print(json.dumps(json.loads(response), indent=4))

def process_post(args):
    val_arg(isinstance(args.url, str), "Invalid type for URL")
    val_arg(args.url != "", "Empty URL provided")

    # Api for coinspot access
    api = CoinSpotApi()

    # Read payload from stdin
    payload = sys.stdin.read()

    # Make request against the API
    response = api.post(args.url, payload, raw_payload=args.raw_input)

    # Display output from the API, formatting if required
    if args.raw_output:
        print(response)
    else:
        print(json.dumps(json.loads(response), indent=4))

def process_args():
    """
    Processes csutl command line arguments
    """

    # Create parser for command line arguments
    parser = argparse.ArgumentParser(
        prog="csutl", description="CoinSpot Utility", exit_on_error=False
    )

    # Parser configuration
    parser.add_argument(
        "-d", action="store_true", dest="debug", help="Enable debug output"
    )

    parser.set_defaults(call_func=None)
    subparsers = parser.add_subparsers(dest="subcommand")

    # post subcommand
    subcommand_post = subparsers.add_parser(
        "post",
        help="Perform a post request against the CoinSpot API"
    )
    subcommand_post.set_defaults(call_func=process_post)

    subcommand_post.add_argument("url", help="URL endpoint")
    subcommand_post.add_argument("-r", action="store_true", dest="raw_output", help="Raw (unpretty) json output")
    subcommand_post.add_argument("--raw-input", action="store_true", dest="raw_input", help="Don't parse input or add nonce")

    # get subcommand
    subcommand_get = subparsers.add_parser(
        "get",
        help="Perform a get request against the CoinSpot API"
    )
    subcommand_get.set_defaults(call_func=process_get)

    subcommand_get.add_argument("url", help="URL endpoint")
    subcommand_get.add_argument("-r", action="store_true", dest="raw_output", help="Raw (unpretty) json output")

    # Parse arguments
    args = parser.parse_args()

    # Capture argument options
    global debug
    debug = args.debug

    # Logging configuration
    level = logging.INFO
    if debug:
        level = logging.DEBUG

    logging.basicConfig(level=level, format="%(levelname)s: %(message)s")

    # Run the sub command
    if args.call_func is None:
        logger.error("Missing subcommand")
        return 1

    return args.call_func(args)

def main():
    ret = 0

    try:
        process_args()

    except BrokenPipeError as e:
        try:
            print("Broken Pipe", file=sys.stderr)
            if not sys.stderr.closed:
                sys.stderr.close()
        except:
            pass

        ret = 1

    except Exception as e: # pylint: disable=board-exception-caught
        if debug:
            logger.error(e, exc_info=True, stack_info=True)
        else:
            logger.error(e)

        ret = 1

    try:
        sys.stdout.flush()
    except Exception as e:
        ret = 1

    sys.exit(ret)

