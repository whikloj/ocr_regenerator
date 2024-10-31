#!/usr/bin/env python3

import argparse
from datetime import datetime
import logging
import os.path
import re
import requests
from urllib.parse import urlparse
import yaml

from fedora.client import FedoraClient


def main():
    parser = argparse.ArgumentParser(description='Check OCR and regen if older than specified date')
    parser.add_argument('-c', '--config', type=str, help='The configuration file to use', required=True)
    parser.add_argument('-d', '--date', type=str, help='The date to check against', required=True)
    parser.add_argument('pid_or_file', type=str, help='The PID or file of PIDs to check')
    args = parser.parse_args()
    with open(args.config, 'r') as f:
        config = yaml.safe_load(f)
    check_before = datetime.strptime(args.date, '%Y-%m-%d')
    check(args.pid_or_file, config, check_before)

if __name__ == '__main__':
    main()