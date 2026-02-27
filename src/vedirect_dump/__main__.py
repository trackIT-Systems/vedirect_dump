import argparse
import json

from vedirect_dump import query_device


def cli():
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        prog="VE.Direct",
        description="Victron VE.Direct python implementation",
    )
    parser.add_argument(
        "-p",
        "--port",
        type=str,
        default="/dev/ttyUSBvd0",  # This is a custom symlink created by a udev rule to avoid race conditions with celular modems
        help="Path to serial port",
    )

    args = parser.parse_args()

    data = query_device(serial_port=args.port)
    data_json = json.dumps(data)
    print(data_json)


if __name__ == "__main__":
    cli()
