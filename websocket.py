import json

from flask import Flask, make_response
from flask_graphql import GraphQLView
from flask_sockets import Sockets

from graphql_ws.gevent import GeventSubscriptionServer

from schema import schema
import logging

logging.basicConfig(filename='/var/www/flask_graphql/error_log/error_log.txt', level=logging.DEBUG, 
                    format='%(asctime)s %(levelname)s %(name)s %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.debug = True
sockets = Sockets(app)




subscription_server = GeventSubscriptionServer(schema)
app.app_protocol = lambda environ_path_info: 'graphql-ws'


@sockets.route('/subscription')
def echo_socket(ws):
    try:
        logger.error('ok1')
        logger.error(ws)
        subscription_server.handle(ws)
        logger.error('ok2')
        return []
    except Exception as e:
        logger.error('ssssssssssssss')
        logger.error(e)



# https://github.com/graphql-python/graphql-ws
if __name__ == "__main__":
    from gevent import pywsgi
    from geventwebsocket.handler import WebSocketHandler
    server = pywsgi.WSGIServer(('', 7000), app, handler_class=WebSocketHandler)
    print 'Serving at host 0.0.0.0:7000/socket...\n'
    server.serve_forever()