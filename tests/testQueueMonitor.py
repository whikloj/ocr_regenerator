import unittest
from unittest import mock

from queue_monitor import QueueMonitor

def mock_get_queue_enqueue_count(*args, **kwargs):
    if args[0] == 'test_queue':
        return 10

def mock_get_queue_dequeue_count(*args, **kwargs):
    if args[0] == 'test_queue':
        return 5

def mock_get_queue_size(*args, **kwargs):
    if args[0] == 'test_queue':
        return 5
    elif args[0] == 'test_queue2':
        return 10

class QueueMonitorTestCase(unittest.TestCase):

    def test_bad_configs(self):
        configs = [
            {'username': 'user', 'password': 'pass'},
            {'host': 'localhost', 'username': 'user'},
            {'host': 'localhost', 'password': 'pass'},
        ]

        for config in configs:
            with self.assertRaises(KeyError):
                QueueMonitor(config)

    def test_config(self):
        config = {
            'username': 'user',
            'password': 'pass',
            'host': 'localhost',
        }
        monitor = QueueMonitor(config)
        self.assertIsNotNone(monitor)
        self.assertIsInstance(monitor, QueueMonitor)
        monitor.close()

    @mock.patch('local_activemq_api_client.client.ActiveMQClient.get_queue_size', side_effect=mock_get_queue_size)
    def test_get_queue_size(self, mock_enqueue):
        config = {
            'username': 'user',
            'password': 'pass',
            'host': 'localhost',
            'queue_name': ['test_queue']
        }
        monitor = QueueMonitor(config)
        self.assertIsNotNone(monitor)
        self.assertIsInstance(monitor, QueueMonitor)
        self.assertFalse(monitor.queue_size_too_large())
        monitor.close()
        self.assertIn(mock.call('test_queue'), mock_enqueue.call_args_list)
        self.assertEqual(1, len(mock_enqueue.call_args_list))

    @mock.patch('local_activemq_api_client.client.ActiveMQClient.get_queue_size', side_effect=mock_get_queue_size)
    def test_get_queue_size2(self, mock_enqueue):
        config = {
            'username': 'user',
            'password': 'pass',
            'host': 'localhost',
            'max_queue_size': 5,
            'queue_name': ['test_queue2']
        }
        monitor = QueueMonitor(config)
        self.assertIsNotNone(monitor)
        self.assertIsInstance(monitor, QueueMonitor)
        self.assertTrue(monitor.queue_size_too_large())
        monitor.close()
        self.assertIn(mock.call('test_queue2'), mock_enqueue.call_args_list)
        self.assertEqual(1, len(mock_enqueue.call_args_list))

    @mock.patch('local_activemq_api_client.client.ActiveMQClient.get_queue_size', side_effect=mock_get_queue_size)
    def test_get_queue_size3(self, mock_enqueue):
        config = {
            'username': 'user',
            'password': 'pass',
            'host': 'localhost',
            'max_queue_size': 5,
            'queue_name': ['test_queue', 'test_queue2']
        }
        monitor = QueueMonitor(config)
        self.assertIsNotNone(monitor)
        self.assertIsInstance(monitor, QueueMonitor)
        self.assertTrue(monitor.queue_size_too_large())
        monitor.close()
        self.assertIn(mock.call('test_queue'), mock_enqueue.call_args_list)
        self.assertIn(mock.call('test_queue2'), mock_enqueue.call_args_list)
        self.assertEqual(2, len(mock_enqueue.call_args_list))

    @mock.patch('local_activemq_api_client.client.ActiveMQClient.get_queue_size', side_effect=mock_get_queue_size)
    def test_get_queue_size4(self, mock_enqueue):
        config = {
            'username': 'user',
            'password': 'pass',
            'host': 'localhost',
            'max_queue_size': 11,
            'queue_name': [
                'test_queue',
                'test_queue2'
            ]
        }
        monitor = QueueMonitor(config)
        self.assertIsNotNone(monitor)
        self.assertIsInstance(monitor, QueueMonitor)
        self.assertFalse(monitor.queue_size_too_large())
        monitor.close()
        self.assertIn(mock.call('test_queue'), mock_enqueue.call_args_list)
        self.assertIn(mock.call('test_queue2'), mock_enqueue.call_args_list)
        self.assertEqual(2, len(mock_enqueue.call_args_list))

    """
    def test_live(self):
        # This test runs against a live ActiveMQ server
        config = {
            'host': 'http://localhost:8161',
            'username': 'admin',
            'password': 'admin',
            'queue_name': 'test_queue'
        }
        monitor = QueueMonitor(config)
        self.assertIsNotNone(monitor)
        self.assertIsInstance(monitor, QueueMonitor)
        self.assertEqual(1, monitor.get_queue_size())
        monitor.close()
    """

if __name__ == "__main__":
    unittest.main()
