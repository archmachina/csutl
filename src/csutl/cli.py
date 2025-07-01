
import argparse
import logging
import sys
import json

from .common import val_arg, val_run
from .api import CoinSpotApi

logger = logging.getLogger(__name__)

debug = False

def process_get(args):
    """
    Handle get type requests for the public api
    """

    # Process incoming arguments
    val_arg(isinstance(args.url, str), "Invalid type for URL")
    val_arg(args.url != "", "Empty URL provided")

    # Api for coinspot access
    api = CoinSpotApi()

    # Make request against the API
    response = api.get(args.url, raw_output=args.raw_output)

    # Display output from the API, formatting if required
    print_output(args, response)

def process_post(args):
    """
    Process post type requests for the private and read-only api
    """

    # Process incoming arguments
    val_arg(isinstance(args.url, str), "Invalid type for URL")
    val_arg(args.url != "", "Empty URL provided")

    # Api for coinspot access
    api = CoinSpotApi()

    # Read payload from stdin
    payload = sys.stdin.read()

    # Make request against the API
    response = api.post(args.url, payload, raw_payload=args.raw_input, raw_output=args.raw_output)

    # Display output from the API, formatting if required
    print_output(args, response)

def process_balance(args):
    """
    Process request to display balances for the account
    """

    # Api for coinspot access
    api = CoinSpotApi()

    url = "/api/v2/ro/my/balances"

    if args.cointype is not None:
        val_arg(isinstance(args.cointype, str), "Invalid cointype supplied")
        val_arg(args.cointype != "", "Empty coin type provided")

        url = f"/api/v2/ro/my/balance/{args.cointype}?available=yes"

    # Request balance info
    response = api.post(url, "{}", raw_output=args.raw_output)

    print_output(args, response)

def process_price_history(args):
    """
    Process request to display price history for a coin type
    """

    # Validate incoming arguments
    val_arg(isinstance(args.cointype, str) and args.cointype != "", "Invalid cointype supplied")
    val_arg(args.age > 0, "Invalid age supplied")
    val_arg(isinstance(args.interval, str), "Invalid value for interval")
    val_arg(args.interval == "hours" or args.interval == "days", "Invalid value for interval")

    # Api for coinspot access
    api = CoinSpotApi()

    # Calculate age for query
    age_hours = args.age
    if args.interval == "days":
        age_hours = age_hours * 24

    # Request balance info
    response = api.get_price_history(args.cointype, age_hours=age_hours, stats=args.stats)

    print_output(args, response)

def process_order_history(args):
    """
    Process request to display order history for the account
    """

    # Api for coinspot access
    api = CoinSpotApi()

    url = "/api/v2/ro/my/orders/completed"

    request = {
        "limit": 200
    }

    # Limit to coin type, if requested
    if args.cointype is not None:
        val_arg(isinstance(args.cointype, str), "Invalid type for cointype")

        request["cointype"] = args.cointype

    # Adjust limit
    if args.limit is not None:
        val_arg(isinstance(args.limit, int), "Invalid type for limit")
        # Don't validate the limit range - Let the api endpoint do this

        request["limit"] = args.limit

    # Start date
    if args.start_date is not None:
        val_arg(isinstance(args.start_date, str), "Invalid type for start date")

        request["startdate"] = args.start_date

    # End date
    if args.end_date is not None:
        val_arg(isinstance(args.end_date, str), "Invalid type for end date")

        request["enddate"] = args.end_date

    # Request order history
    response = api.post(url, request, raw_output=args.raw_output)

    print_output(args, response)

def add_common_args(parser):
    """
    Common arguments for all subcommands
    """

    # Process incoming arguments
    val_arg(isinstance(parser, argparse.ArgumentParser), "Invalid parser supplied to add_common_args")

    # Debug option
    parser.add_argument(
        "-d", action="store_true", dest="debug", help="Enable debug output"
    )

    # Json formatting options
    parser.add_argument("--raw-output", action="store_true", dest="raw_output", help="Raw (unpretty) json output")

def print_output(args, output):
    """
    Display the response output, with option to display raw or pretty formatted
    """

    # Process incoming arguments
    val_arg(isinstance(args.raw_output, bool), "Invalid type for raw_output")
    val_arg(isinstance(output, str), "Invalid output supplied to print_output")

    # Display output raw or pretty
    if args.raw_output:
        print(output)
    else:
        print(json.dumps(json.loads(output), indent=4))

def process_args():
    """
    Processes csutl command line arguments
    """

    # Create parser for command line arguments
    parser = argparse.ArgumentParser(
        prog="csutl", description="CoinSpot Utility", exit_on_error=False
    )

    parser.set_defaults(debug=False)

    # Parser configuration
    #parser.add_argument(
    #    "-d", action="store_true", dest="debug", help="Enable debug output"
    #)

    parser.set_defaults(call_func=None)
    subparsers = parser.add_subparsers(dest="subcommand")

    # post subcommand
    subcommand_post = subparsers.add_parser(
        "post",
        help="Perform a post request against the CoinSpot API"
    )
    subcommand_post.set_defaults(call_func=process_post)
    add_common_args(subcommand_post)

    subcommand_post.add_argument("url", help="URL endpoint")
    subcommand_post.add_argument("--raw-input", action="store_true", dest="raw_input", help="Don't parse input or add nonce")

    # get subcommand
    subcommand_get = subparsers.add_parser(
        "get",
        help="Perform a get request against the CoinSpot API"
    )
    subcommand_get.set_defaults(call_func=process_get)
    add_common_args(subcommand_get)

    subcommand_get.add_argument("url", help="URL endpoint")

    # Balance
    subcommand_balance = subparsers.add_parser(
        "balance",
        help="Retrieve account balance"
    )
    subcommand_balance.set_defaults(call_func=process_balance)
    add_common_args(subcommand_balance)

    subcommand_balance.add_argument("-t", action="store", dest="cointype", help="Coin type", default=None)

    # Price history
    subcommand_price_history = subparsers.add_parser(
        "price_history",
        help="Retrieve price history"
    )
    subcommand_price_history.set_defaults(call_func=process_price_history)
    add_common_args(subcommand_price_history)

    subcommand_price_history.add_argument("-s", action="store_true", dest="stats", help="Display stats")
    subcommand_price_history.add_argument("-a", action="store", dest="age", type=int, help="Age", default=1)
    subcommand_price_history.add_argument("-i", action="store", dest="interval", type=str, help="Interval - days or hours", choices=["days", "hours"], default="hours")
    subcommand_price_history.add_argument("cointype", action="store", help="Coin type")

    # order history
    subcommand_order_history = subparsers.add_parser(
        "order_history",
        help="Retrieve account order history"
    )
    subcommand_order_history.set_defaults(call_func=process_order_history)
    add_common_args(subcommand_order_history)

    subcommand_order_history.add_argument("-s", action="store", dest="start_date", help="Start date", default=None)
    subcommand_order_history.add_argument("-e", action="store", dest="end_date", help="End date", default=None)
    subcommand_order_history.add_argument("-l", action="store", dest="limit", help="Result limit (default 200, max 500)", type=int, default=None)
    subcommand_order_history.add_argument("-t", action="store", dest="cointype", help="coin type", default=None)

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

