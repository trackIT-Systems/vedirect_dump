import logging

from vedirect_m8.vedirect import Vedirect

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


def map_keys(packet) -> dict[str, int | float | str]:
    data = {}
    for key, value in packet.items():
        try:
            # Meanings can be found in https://www.victronenergy.com/upload/documents/VE.Direct-Protocol-3.33.pdf
            match key:
                case "PID":
                    data["Product ID"] = value
                case "FW":
                    data["Firmware version"] = int(value) / 100
                case "SER#":
                    data["Serial number"] = value
                case "V":
                    data["Channel 1 voltage (V)"] = int(value) * 0.001
                case "I":
                    data["Channel 1 current (A)"] = int(value) * 0.001
                case "VPV":
                    data["Input Voltage (V)"] = int(value) * 0.001
                case "PPV":
                    data["Input power (W)"] = int(value)
                case "IL":
                    data["Load output actual current"] = int(value) * 0.001
                case "H19":
                    data["Yield total (kWh)"] = float(value) * 0.01
                case "H20":
                    data["Yield today (kWh)"] = float(value) * 0.01
                case "H21":
                    data["Maximum power today (W)"] = int(value)
                case "H22":
                    data["Yield yesterday (kWh)"] = float(value) * 0.01
                case "H23":
                    data["Maximum power yesterday (W)"] = int(value)
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
                    logging.warning("Key is not known [{key=%s}, {value=%s}]", key, value)
                    data[key] = value
        except Exception as ex:
            logging.warning("Exception parsing value [{key=%s}, {value=%s}], %s", key, value, ex)

    return data


def query_device(serial_port: str = "/dev/ttyUSB0") -> dict[str, int | float | str]:
    ve = Vedirect(serial_conf={"serial_port": serial_port}, max_packet_blocks=None)

    packet = ve.read_global_packet()
    data = map_keys(packet)
    return data
