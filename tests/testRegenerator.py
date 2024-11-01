import unittest
from datetime import datetime
from os.path import dirname
from unittest import mock

from ocr import OcrRegenerator


class MockResponse:
    def __init__(self, content, status_code):
        self.content = content
        self.status_code = status_code


# This method will be used by the mock to replace requests.get
def mocked_requests(*args, **kwargs):
    if args[0] == 'http://localhost:8080/fcrepo/objects/test:pid/datastreams?format=xml&profiles=true':
        with open(dirname(__file__) + '/resources/list_datastreams_profile.xml', 'rb') as f:
            return MockResponse(f.read(), 200)
    elif args[0] == 'http://localhost:8080/ocr/test:pid':
        return MockResponse(None, 204)

    return MockResponse(None, 404)


class RegeneratorTest(unittest.TestCase):

    def test_setup(self):
        config = {
            'fedora': {
                'url': 'http://localhost:8080/fcrepo/',
                'username': 'user',
                'password': 'pass'
            },
            'regenerator': {
                'url': 'http://localhost:8080/ocr',
            },
            'queue_monitor': {
                'host': 'localhost',
                'username': 'user',
                'password': 'pass',
                'queue_name': 'queue'
            }
        }
        regen = OcrRegenerator(config, datetime.now())
        self.assertIsNotNone(regen)
        self.assertIsInstance(regen, OcrRegenerator)

    def test_setup_fail(self):
        configs = [
            {
                'fedora': {
                    'url': 'http://localhost:8080/fcrepo/',
                    'username': 'user',
                    'password': 'pass'
                },
                'queue_monitor': {
                    'host': 'localhost',
                    'username': 'user',
                    'password': 'pass',
                    'queue_name': 'queue'
                }
            },
            {
                'regenerator': {
                    'url': 'http://localhost:8080/ocr',
                },
                'queue_monitor': {
                    'host': 'localhost',
                    'username': 'user',
                    'password': 'pass',
                    'queue_name': 'queue'
                }
            },
            {
                'fedora': {
                    'url': 'http://localhost:8080/fcrepo/',
                    'username': 'user',
                    'password': 'pass'
                },
                'regenerator': {
                    'url': 'http://localhost:8080/ocr',
                },
            }
        ]

        for config in configs:
            with self.assertRaises(KeyError):
                OcrRegenerator(config, datetime.now())


    @mock.patch('fedora.client.requests.get', side_effect=mocked_requests)
    @mock.patch('ocr.regenerator.requests.get', side_effect=mocked_requests)
    def test_single_pid(self, mock_regen, mock_fedora):
        # decorators are applied bottom to top, so the calls all seem to appear in the last mock.
        config = {
            'fedora': {
                'url': 'http://localhost:8080/fcrepo/',
                'username': 'user',
                'password': 'pass'
            },
            'regenerator': {
                'url': 'http://localhost:8080/ocr',
            },
            'queue_monitor': {
                'host': 'localhost',
                'username': 'user',
                'password': 'pass',
                'queue_name': 'queue'
            }
        }
        today = datetime.now()
        regen = OcrRegenerator(config, today)
        regen.check('test:pid')
        self.assertIn(
            mock.call('http://localhost:8080/fcrepo/objects/test:pid/datastreams?format=xml&profiles=true', auth=('user', 'pass')),
            mock_fedora.call_args_list
        )
        self.assertIn(
            mock.call('http://localhost:8080/ocr/test:pid'),
            mock_fedora.call_args_list
        )
        self.assertEqual(2, len(mock_fedora.call_args_list))
        self.assertEqual(0, len(mock_regen.call_args_list))

    @mock.patch('fedora.client.requests.get', side_effect=mocked_requests)
    @mock.patch('ocr.regenerator.requests.get', side_effect=mocked_requests)
    def test_single_pid_old(self, mock_regen, mock_fedora):
        config = {
            'fedora': {
                'url': 'http://localhost:8080/fcrepo/',
                'username': 'user',
                'password': 'pass'
            },
            'regenerator': {
                'url': 'http://localhost:8080/ocr',
            },
            'queue_monitor': {
                'host': 'localhost',
                'username': 'user',
                'password': 'pass',
                'queue_name': 'queue'
            }
        }
        today = datetime.strptime('2010-01-01', '%Y-%m-%d')
        regen = OcrRegenerator(config, today)
        regen.check('test:pid')
        self.assertIn(
            mock.call('http://localhost:8080/fcrepo/objects/test:pid/datastreams?format=xml&profiles=true',
                      auth=('user', 'pass')),
            mock_fedora.call_args_list
        )
        self.assertNotIn(
            mock.call('http://localhost:8080/ocr/test:pid'),
            mock_fedora.call_args_list
        )
        self.assertEqual(1, len(mock_fedora.call_args_list))
        self.assertEqual(0, len(mock_regen.call_args_list))

if __name__ == "__main__":
    unittest.main()
