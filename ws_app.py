from flask import Flask
from flask_sockets import Sockets
from graphql_subscriptions import (
    SubscriptionManager,
    RedisPubsub,
    SubscriptionServer
)
from schema import schema
import logging
import threading
from time import sleep

logging.basicConfig(filename='/var/www/flask_graphql/error_log/error_log.txt', level=logging.DEBUG, 
                    format='%(asctime)s %(levelname)s %(name)s %(message)s')
logger = logging.getLogger(__name__)



app = Flask(__name__)

# using Flask Sockets here, but could use gevent-websocket directly
# to create a websocket app and attach it to flask app object
sockets = Sockets(app)

# instantiate pubsub -- this will be used to "publish" mutations
# and also to pass it into your subscription manager
pubsub = RedisPubsub()

# instantiate subscription manager object -- passing in schema and pubsub
subscription_mgr = SubscriptionManager(schema, pubsub)

# using Flask Sockets here -- on each new connection instantiate a
# subscription app / server -- passing in subscription manager and websocket
@sockets.route('/socket')
def socket_channel(websocket):
    try:
        subscription_server = SubscriptionServer(subscription_mgr, websocket)
        subscription_server.handle()
        logger.error('connection here')
        logger.error(subscription_server)
        logger.error('connection here 222')
        return {"Status Code": "200 OK"}
    except Exception as e:
        logger.error('ssssssssssssss')
        logger.error(e)


if __name__ == "__main__":

    # using a gevent webserver so multiple connections can be
    # maintained concurrently -- gevent websocket spawns a new
    # greenlet for each request and forwards the request to flask
    # app or socket app, depending on request type
    from geventwebsocket import WebSocketServer

    try:
        # ws = WebSocketServer(('', 7000), app)
        # wst = threading.Thread(target=ws.serve_forever)
        # wst.daemon = True
        # wst.start()

        # conn_timeout = 5
        # while not ws.sock.connected and conn_timeout:
        #     sleep(1)
        #     conn_timeout -= 1

        # msg_counter = 0
        # while ws.sock.connected:
        #     ws.send('Hello world %d'%msg_counter)
        #     sleep(1)
        #     msg_counter += 1

        server = WebSocketServer(('', 7000), app)
        print 'Serving at host 0.0.0.0:7000/socket...\n'
        server.serve_forever()
    except Exception as e:
        logger.error(e)

