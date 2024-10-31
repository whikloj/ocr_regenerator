import logging
import os
import re
from datetime import datetime
import requests
import time
from urllib.parse import urlparse

from fedora.client import FedoraClient


class OcrRegenerator:

    def __init__(self, config: dict, check_before: datetime):
        self.config = config
        fedora_config = config['fedora']
        self.client = FedoraClient(fedora_config['url'], fedora_config['username'], fedora_config['password'])
        regen = config['regenerator']
        self.ocr_gen_url = regen['url'].strip().rstrip('/')
        self.batch_size = regen.get('batch_size', 10)
        self.delay_seconds = regen.get('delay_seconds', 30)
        urlparse(self.ocr_gen_url)
        self.logger = self._setup_logging()
        self.check_before = check_before

    def set_logging_level(self, level: int):
        self.logger.setLevel(level)

    def set_check_before(self, check_before: datetime):
        if check_before is not None and check_before < datetime.now():
            self.check_before = check_before
        else:
            raise ValueError('Check before must be a datetime in the past')

    def check(self, path):
        if os.path.exists(path):
            self._check_file(path)
        else:
            self._check_for_ocr(path)

    def _check_file(self, file_path):
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                lines = f.readlines()
                for i, line in enumerate(lines):
                    if i % self.batch_size == 0 and i != 0:
                        self.logger.debug(f'Sleeping for {self.delay_seconds} seconds')
                        time.sleep(self.delay_seconds)
                    self._check_for_ocr(line)

    def _check_for_ocr(self, pid: str) -> bool:
        pid = pid.strip()
        if self._validate_pid(pid):
            datastreams = self.client.list_datastreams(pid, profiles=True)
            ocr = None
            for ds in datastreams:
                if ds.dsid == 'OCR':
                    ocr = ds
                    break
            if ocr is not None:
                self.logger.debug(f'OCR for {pid} is {ocr.created_date}')
                if ocr.get_created_date() < self.check_before:
                    self.logger.debug(f'Regenerating OCR for {pid}')
                    result = self._regenerate_ocr(pid)
                    if result:
                        self.logger.info(f'Regenerated OCR for {pid}')
                        return True
                    else:
                        self.logger.error(f'Failed to regenerate OCR for {pid}')
                else:
                    self.logger.info(f'OCR for {pid} is up to date')
            else:
                self.logger.info(f'No OCR datastream for {pid}')
            return False

    def _regenerate_ocr(self, pid: str) -> bool:
        res = requests.get(f'{self.ocr_gen_url}/{pid}')
        self.logger.debug(f'Regenerate OCR response: {res.status_code}')
        return 200 <= res.status_code < 400

    @staticmethod
    def _validate_pid(pid: str) -> bool:
        return re.match('^[^:]+:[^:]+$', pid.strip()) is not None

    @staticmethod
    def _setup_logging() -> logging.Logger:
        logging.basicConfig(
            filename="./ocrRegenerator.log",
            level=logging.INFO,
            format='%(asctime)s %(levelname)s:%(message)s',
            datefmt='%m/%d/%Y %I:%M:%S %p'
        )
        return logging.getLogger()
