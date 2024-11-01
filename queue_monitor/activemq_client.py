from local_activemq_api_client.client import ActiveMQClient

class QueueMonitor:
    def __init__(self, config: dict):
        self.config = config
        # Create an ActiveMQClient instance
        self.client = ActiveMQClient(config['host'], config['username'], config['password'])

    def get_queue_size(self):
        # Get the number of messages in the queue
        return self.client.get_queue_size(self.config['queue_name'])

    def close(self):
        self.client.close()
