import json

import pika
from pika import connection

from xprint import xprint


class ShoppingEventProducer:

    def __init__(self):
        # Do not edit the init method.
        # Set the variables appropriately in the methods below.
        self.connection = None
        self.channel = None

    def initialize_rabbitmq(self):
        # To implement - Initialize the RabbitMq connection, channel, exchange and queue here
        conn = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        ch   = conn.channel()
        self.channel = ch
        self.connection = conn
        
        self.channel.exchange_declare(exchange="shopping_events_exchange", exchange_type="x-consistent-hash", durable=True)
        
        #ch.queue_bind(exchange="shopping_events_exchange", queue="shopping_dead_letter_queue", routing_key="1")

        xprint("ShoppingEventProducer initialize_rabbitmq() called")

    def publish(self, shopping_event):
        xprint("ShoppingEventProducer: Publishing shopping event {}".format(vars(shopping_event)))
        # To implement - publish a message to the Rabbitmq here
        # Use json.dumps(vars(shopping_event)) to convert the shopping_event object to JSON
        shopping_event_json = json.dumps(vars(shopping_event))
        self.channel.basic_publish(exchange="shopping_events_exchange", routing_key=shopping_event.product_number, body=shopping_event_json)
        
    def close(self):
        # Do not edit this method
        self.channel.close()
        self.connection.close()
