from local_activemq_api_client.client import ActiveMQClient

class QueueMonitor:
    def __init__(self, config: dict):
        self.config = config
        self.max_queue_size = config.get('max_queue_size', 100)
        self.queues = config.get('queue_name', [])
        # Create an ActiveMQClient instance
        self.client = ActiveMQClient(config['host'], config['username'], config['password'])

    def queue_size_too_large(self):
        """ Get the number of messages in the queue and if too large return True """
        for queue in self.queues:
            if self.client.get_queue_size(queue) > self.max_queue_size:
                return True
        return False

    def close(self):
        self.client.close()
