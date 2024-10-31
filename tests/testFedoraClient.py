import unittest
from os.path import dirname
from unittest import mock

from fedora import FedoraClient

# This method will be used by the mock to replace requests.get
def mocked_requests_get(*args, **kwargs):
    class MockResponse:
        def __init__(self, content, status_code):
            self.content = content
            self.status_code = status_code

    if args[0] == 'http://localhost:8080/fcrepo/objects/test:pid/datastreams?format=xml':
        with open(dirname(__file__) + '/resources/list_datastreams.xml', 'rb') as f:
            return MockResponse(f.read(), 200)
    elif args[0] == 'http://localhost:8080/fcrepo/objects/test:pid/datastreams?format=xml&profiles=true':
        with open(dirname(__file__) + '/resources/list_datastreams_profile.xml', 'rb') as f:
            return MockResponse(f.read(), 200)

    return MockResponse(None, 404)


class FedoraClientTest(unittest.TestCase):

    def test_bad_url(self):
        self.assertRaises(Exception, FedoraClient, ['bob', 'user', 'pass'])

    def test_good_url(self):
        client = FedoraClient('http://localhost:8080/fcrepo/', 'user', 'pass')
        self.assertIsNotNone(client)

    @mock.patch('fedora.client.requests.get', side_effect=mocked_requests_get)
    def test_list_datastreams(self, mock_get):
        client = FedoraClient('http://localhost:8080/fcrepo/', 'user', 'pass')
        datastreams = client.list_datastreams('test:pid')
        self.assertEqual(15, len(datastreams))

    @mock.patch('fedora.client.requests.get', side_effect=mocked_requests_get)
    def test_list_datastreams_profile(self, mock_get):
        client = FedoraClient('http://localhost:8080/fcrepo/', 'user', 'pass')
        datastreams = client.list_datastreams('test:pid', profiles=True)
        self.assertEqual(15, len(datastreams))


if __name__ == "__main__":
    unittest.main()
