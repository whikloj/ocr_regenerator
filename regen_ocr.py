#!/usr/bin/env python3

import argparse
from datetime import datetime
import yaml

from ocr import OcrRegenerator


def main():
    parser = argparse.ArgumentParser(description='Check OCR and regen if older than specified date')
    parser.add_argument('-c', '--config', type=str, help='The configuration file to use', required=True)
    parser.add_argument('-d', '--date', type=str, help='The date to check against', required=True)
    parser.add_argument('pid_or_file', type=str, help='The PID or file of PIDs to check')
    args = parser.parse_args()
    with open(args.config, 'r') as f:
        config = yaml.safe_load(f)
    check_before = datetime.strptime(args.date, '%Y-%m-%d')
    regen = OcrRegenerator(config, check_before)
    regen.check(args.pid_or_file)

if __name__ == '__main__':
    main()