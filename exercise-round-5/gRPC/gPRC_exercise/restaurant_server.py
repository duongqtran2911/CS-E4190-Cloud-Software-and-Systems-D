import grpc
import sys
from concurrent import futures
from proto import restaurant_pb2
from proto import restaurant_pb2_grpc

RESTAURANT_ITEMS_FOOD = ["chips", "fish", "burger", "pizza", "pasta", "salad"]
RESTAURANT_ITEMS_DRINK = ["water", "fizzy drink", "juice", "smoothie", "coffee", "beer"]
RESTAURANT_ITEMS_DESSERT = ["ice cream", "chocolate cake", "cheese cake", "brownie", "pancakes", "waffles"]

class Restaurant(restaurant_pb2_grpc.RestaurantServicer):

    # Logic goes here
    def FoodOrder(self, request, context):
        for item in request.items:
            if item not in RESTAURANT_ITEMS_FOOD:
                return restaurant_pb2.RestaurantResponse(orderID = request.orderID, status=1)
        return restaurant_pb2.RestaurantResponse(orderID=request.orderID, status=0)
    
    def DrinkOrder(self, request, context):
        for item in request.items:
            if item not in RESTAURANT_ITEMS_DRINK:
                return restaurant_pb2.RestaurantResponse(orderID = request.orderID, status=1)
        return restaurant_pb2.RestaurantResponse(orderID = request.orderID, status=0)

    def DessertOrder(self, request, context):
        for item in request.items:
            if item not in RESTAURANT_ITEMS_DESSERT:
                return restaurant_pb2.RestaurantResponse(orderID = request.orderID, status=1)
        return restaurant_pb2.RestaurantResponse(orderID = request.orderID, status=0)


def serve():

    # Logic goes here
    # Remember to start the server on localhost and a port defined by the first command line argument
    port = 'localhost:{0}'.format(sys.argv[1])
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    restaurant_pb2_grpc.add_RestaurantServicer_to_server(Restaurant(), server)
    server.add_insecure_port(port)
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    serve()
