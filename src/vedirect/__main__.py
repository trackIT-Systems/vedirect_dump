import argparse
import json

from vedirect_m8.vedirect import Vedirect


def parse_arguments() -> argparse.Namespace:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        prog="VE.Direct",
        description="Victron VE.Direct python implementation",
    )
    parser.add_argument(
        "port",
        type=str,
        help="Path to serial port",
    )

    return parser.parse_args()


cs_mapping: dict[str, str] = {
    "0": "Off",
    "2": "Fault",
    "3": "Bulk",
    "4": "Absorption",
    "5": "Float",
    "7": "Equalize (manual)",
    "245": "Starting-up",
    "247": "Auto equalize / Recondition",
    "252": "External Control",
}

mppt_mapping: dict[str, str] = {
    "0": "Off",
    "1": "Voltage or current limited",
    "2": "MPP Tracker active",
}

or_mapping: dict[str, str] = {
    "0x00000001": "No input power",
    "0x00000002": "Switched off (power switch)",
    "0x00000004": "Switched off (device mode register)",
    "0x00000008": "Remote input",
    "0x00000010": "Protection active",
    "0x00000020": "Paygo",
    "0x00000040": "BMS",
    "0x00000080": "Engine shutdown detection",
    "0x00000100": "Analysing input voltage",
}

err_mapping: dict[str, str] = {
    "0": "No error",
    "2": "Battery voltage too high",
    "17": "Charger temperature too high",
    "18": "Charger over current",
    "19": "Charger current reversed",
    "20": "Bulk time limit exceeded",
    "21": "Current sensor issue (sensor bias/sensor broken)",
    "26": "Terminals overheated",
    "28": "Converter issue (dual converter models only)",
    "33": "Input voltage too high (solar panel)",
    "34": "Input current too high (solar panel)",
    "38": "Input shutdown (due to excessive battery voltage)",
    "39": "Input shutdown (due to current flow during off mode)",
    "65": "Lost communication with one of devices",
    "66": "Synchronised charging device configuration issue",
    "67": "BMS connection lost",
    "68": "Network misconfigured",
    "116": "Factory calibration data lost",
    "117": "Invalid/incompatible firmware",
    "119": "User settings invalid",
}

unknown = "Unknown"


def prepare_data_callback(packet):
    data = {}
    for key, value in packet.items():
        match key:
            case "PID":
                # Meaning can be found in https://www.victronenergy.com/upload/documents/VE.Direct-Protocol-3.33.pdf
                data["Product ID"] = value
            case "FW":
                # Meaning can be found in https://www.victronenergy.com/upload/documents/VE.Direct-Protocol-3.33.pdf
                data["Firmware version"] = value
            case "SER#":
                # Meaning can be found in https://www.victronenergy.com/upload/documents/VE.Direct-Protocol-3.33.pdf
                data["Serial number"] = value
            case "V":
                data["Channel 1 voltage (V)"] = int(value) * 0.01
            case "I":
                data["Channel 1 current (A)"] = int(value) * 0.01
            case "VPV":
                data["Input Voltage (V)"] = int(value) * 0.01
            case "PPV":
                data["Input current"] = int(value) * 0.01
            case "IL":
                data["Load output actual current"] = int(value) * 0.01
            case "H19":
                data["Yield total"] = float(value)
            case "H20":
                data["Yield today"] = float(value)
            case "H21":
                data["Maximum power today"] = int(value)
            case "H22":
                data["Yield yesterday"] = float(value)
            case "H23":
                data["Maximum power yesterday"] = int(value)
            case "HSDS":
                data["Day sequence number"] = int(value)
            case "CS":
                data["Operation state"] = cs_mapping.get(value, unknown)
            case "MPPT":
                data["Tracker operation mode"] = mppt_mapping.get(value, unknown)
            case "OR":
                data["Off reason"] = or_mapping.get(value, unknown)
            case "ERR":
                data["Error code"] = err_mapping.get(value, unknown)
            case "LOAD":
                data["Load output status"] = "On" if value == "0" else "Off"
            case _:
                print(f"Key is not known [{key=}, {value=}]")

    print(json.dumps(data))


def cli():
    args: argparse.Namespace = parse_arguments()
    ve = Vedirect(serial_conf={"serial_port": args.port}, max_packet_blocks=None)
    ve.read_data_callback(prepare_data_callback, max_loops=1)


if __name__ == "__main__":
    cli()
