#!/usr/bin/env python3

import argparse
from datetime import datetime
import json
import os.path
import sys


def parse(log_file):
    """
    Parse log file generated by the pidstat command to get average CPU usage.
    """
    if not os.path.isfile(log_file):
        raise FileNotFoundError("{} not found.".format(log_file))

    with open(log_file) as f:
        content = f.readlines()

    cpu_usage = 0
    if len(content) > 3:
        # Ignore first 3 header lines
        for line in content[3:]:
            try:
                # Get 8th element (CPU%)
                cpu_task = float(line.split()[7])
                cpu_usage += cpu_task
            except IndexError as exc:
                raise RuntimeError("Cannot find CPU% data.") from exc
            except ValueError as exc:
                raise RuntimeError("Incorrect value for CPU%.") from exc
    else:
        raise RuntimeError(
            (
                "{} should contain at least 3 lines, but contains {} "
                "lines instead.".format(log_file, len(content))
            )
        )
    return cpu_usage


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Parse log files containing pidstat data."
    )
    parser.add_argument(
        "logfiles", nargs=2, help="Path to the 2 log files to parse."
    )
    parser.add_argument(
        "--json", action="store_true", help="Output parsed info as json."
    )
    args = parser.parse_args()
    cpu_averages = []
    for logfile in args.logfiles:
        cpu_avg = parse(logfile)
        if cpu_avg == 0:
            sys.exit(
                "CPU usage reported is 0%. There is probably something wrong!"
            )
        cpu_averages.append(cpu_avg)
        if not args.json:
            print(
                "Processes in {} used {:.2f}% CPU.".format(logfile, cpu_avg)
            )
    if args.json:
        output = {
            "date": datetime.utcnow().isoformat(),
            "cpu_before": cpu_averages[0],
            "cpu_after": cpu_averages[1],
        }
        print(json.dumps(output))
    else:
        if cpu_averages[0] > cpu_averages[1]:
            print()
            print("CPU usage is lower after compared to before.")
        else:
            print()
            sys.exit("Error: CPU usage is higher after compared to before.")
