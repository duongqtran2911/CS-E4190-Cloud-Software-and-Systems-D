from types import SimpleNamespace

import pika
import json
import dateutil.parser
import time

from pika.spec import Channel
from db_and_event_definitions import customers_database, cost_per_unit, number_of_units, BillingEvent, ProductEvent
from xprint import xprint

class ShoppingWorker:

    def __init__(self, worker_id, queue, weight="1"):
        # Do not edit the init method.
        # Set the variables appropriately in the methods below.
        self.connection = None
        self.channel = None
        self.worker_id = worker_id
        self.queue = queue
        self.weight = weight
        self.shopping_state = {}
        self.shopping_events = []
        self.billing_event_producer = None
        self.customer_app_event_producer = None

    def initialize_rabbitmq(self):
        # To implement - Initialize the RabbitMQ connection, channel, exchange and queue here
        # Also initialize the channels for the billing_event_producer and customer_app_event_producer
        conn = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        ch = conn.channel()
        self.channel = ch
        self.connection = conn
        
        self.channel.exchange_declare(exchange="shopping_events_exchange", exchange_type="x-consistent-hash", durable=True)
        
        self.channel.exchange_declare(exchange="dead-letter-exchange", exchange_type="direct", durable=True)
        
        self.channel.exchange_declare(exchange="customer_app_events", exchange_type="topic", durable=True)
        
        self.channel.queue_declare(queue=self.queue, durable=True, arguments={"x-dead-letter-exchange":"dead-letter-exchange", "x-dead-letter-routing-key":"shopping_dead_letter_queue"})
        
        self.channel.queue_declare(queue="shopping_events_dead_letter_queue", durable=True)
        
        self.channel.queue_bind(exchange="dead-letter-exchange", queue="shopping_events_dead_letter_queue", routing_key="shopping_dead_letter_queue")
        
        self.channel.queue_bind(exchange="shopping_events_exchange", queue=self.queue, routing_key=self.weight)
        
        self.billing_event_producer = BillingEventProducer(self.connection, self.worker_id)
        self.customer_app_event_producer = CustomerEventProducer(self.connection, self.worker_id)      
        
        xprint("ShoppingWorker {}: initialize_rabbitmq() called".format(self.worker_id))

    def handle_shopping_event(self, ch, method, properties, body):
        # To implement - This is the callback that is passed to "on_message_callback" when a message is received
        body_dict = json.loads(body.decode('utf-8'))
        shipping_event = ProductEvent(event_type=body_dict['event_type'], product_number=body_dict['product_number'], timestamp=body_dict['timestamp'])
        customer_id = self.get_customer_id_from_shopping_event(shipping_event)
        
        if(customer_id == None):
            self.channel.basic_reject(delivery_tag=method.delivery_tag, requeue=False)
            return
        
        if(shipping_event.event_type == 'pick up'):
            self.shopping_events.append(shipping_event)
            self.shopping_state[shipping_event.product_number] = shipping_event.timestamp
            #publishing to the customer event exchange.
            xprint("forwarding to the customer app event exchange")
            customer_prod = self.customer_app_event_producer
            customer_prod.initialize_rabbitmq()
            customer_prod.publish_shopping_event(customer_id=customer_id, shopping_event=shipping_event)
        else:
            self.shopping_events.append(shipping_event)
            #clear state and list.
            cost = (number_of_units * cost_per_unit) - ((number_of_units * cost_per_unit) * (20/100))
            
            billing = BillingEvent(customer_id=customer_id, product_number=shipping_event.product_number, pickup_time=self.shopping_state[shipping_event.product_number], purchase_time=shipping_event.timestamp, shopping_cost=cost)
            
            billing_prod = self.billing_event_producer
            billing_prod.initialize_rabbitmq()
            billing_prod.publish(billing_event=billing)
            
            customer_prod = self.customer_app_event_producer
            customer_prod.initialize_rabbitmq()
            customer_prod.publish_billing_event(billing_event=billing)
            customer_prod.publish_shopping_event(customer_id=customer_id, shopping_event=shipping_event)
            self.shopping_state.pop(shipping_event.product_number)
            
        #xprint(method.delivery_tag)
        self.channel.basic_ack(method.delivery_tag)
            
        xprint("ShoppingWorker {}: handle_event() called".format(self.worker_id))
        # Handle the application logic and the publishing of events here

    # Utility function to get the customer_id from a shopping event
    def get_customer_id_from_shopping_event(self, shopping_event):
        customer_id = [customer_id for customer_id, product_number in customers_database.items()
                       if shopping_event.product_number == product_number]
        if len(customer_id) is 0:
            xprint("{}: Customer Id for product number {} Not found".format(self.worker_id, shopping_event.product_number))
            return None
        return customer_id[0]

    def start_consuming(self):
        # To implement - Start consuming from Rabbit
        self.channel.basic_consume(queue=self.queue, on_message_callback=self.handle_shopping_event, auto_ack=False)
        self.channel.start_consuming()
        xprint("ShoppingWorker {}: start_consuming() called".format(self.worker_id))

    def close(self):
        # Do not edit this method
        try:
            xprint("Closing worker with id = {}".format(self.worker_id))
            self.channel.stop_consuming()
            time.sleep(1)
            self.channel.close()
            self.billing_event_producer.close()
            self.customer_app_event_producer.close()
            time.sleep(1)
            self.connection.close()
        except Exception as e:
            print("Exception {} when closing worker with id = {}".format(e, self.worker_id))


class BillingEventProducer:

    def __init__(self, connection, worker_id):
        # Do not edit the init method.
        self.worker_id = worker_id
        # Reusing connection created in ShoppingWorker
        self.channel = connection.channel()

    def initialize_rabbitmq(self):
        # To implement - Initialize the RabbitMq connection, channel, exchange and queue here
        xprint("BillingEventProducer {}: initialize_rabbitmq() called".format(self.worker_id))
        self.channel.queue_declare(queue='billing_events', durable=True)

    def publish(self, billing_event):
        xprint("BillingEventProducer {}: Publishing billing event {}".format(
            self.worker_id,
            vars(billing_event)))
        self.channel.basic_publish(exchange="", routing_key="billing_events", body=json.dumps(vars(billing_event)))
        # To implement - publish a message to the Rabbitmq here
        # Use json.dumps(vars(billing_event)) to convert the shopping_event object to JSON
        

    def close(self):
        # Do not edit this method
        self.channel.close()


class CustomerEventProducer:

    def __init__(self, connection, worker_id):
        # Do not edit the init method.
        self.worker_id = worker_id
        # Reusing connection created in ShoppingWorker
        self.channel = connection.channel()

    def initialize_rabbitmq(self):
        # To implement - Initialize the RabbitMq connection, channel, exchange and queue here
        xprint("CustomerEventProducer {}: initialize_rabbitmq() called".format(self.worker_id))


    def publish_billing_event(self, billing_event):
        xprint("{}: CustomerEventProducer: Publishing billing event {}"
              .format(self.worker_id, vars(billing_event)))
        self.channel.basic_publish(exchange="customer_app_events", routing_key=billing_event.customer_id, body=json.dumps(vars(billing_event)))
        # To implement - publish a message to the Rabbitmq here
        # Use json.dumps(vars(billing_event)) to convert the shopping_event object to JSON

    def publish_shopping_event(self, customer_id, shopping_event):
        xprint("{}: CustomerEventProducer: Publishing shopping event {} {}"
              .format(self.worker_id, customer_id, vars(shopping_event)))
        self.channel.basic_publish(exchange="customer_app_events", routing_key=customer_id, body=json.dumps(vars(shopping_event)))
        # To implement - publish a message to the Rabbitmq here
        # Use json.dumps(vars(shopping_event)) to convert the shopping_event object to JSON

    def close(self):
        # Do not edit this method
        self.channel.close()
