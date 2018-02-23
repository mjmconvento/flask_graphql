from __future__ import absolute_import
from __future__ import print_function
from builtins import object
import copy
import json

from flask import Flask, request, jsonify
from flask_graphql import GraphQLView
from flask_sockets import Sockets
from functools import wraps
from geventwebsocket import WebSocketServer
from promise import Promise
import graphene

from .subscription_manager import SubscriptionManager, RedisPubsub
from .subscription_transport_ws import SubscriptionServer

TEST_PORT = 5000

data = {
    '1': {
        'id': '1',
        'name': 'Dan'
    },
    '2': {
        'id': '2',
        'name': 'Marie'
    },
    '3': {
        'id': '3',
        'name': 'Jessie'
    }
}


class UserType(graphene.ObjectType):
    id = graphene.String()
    name = graphene.String()


class Query(graphene.ObjectType):
    test_string = graphene.String()


class Subscription(graphene.ObjectType):
    user = graphene.Field(UserType, id=graphene.String())
    user_filtered = graphene.Field(UserType, id=graphene.String())
    context = graphene.String()
    error = graphene.String()

    def resolve_user(self, args, context, info):
        id = args['id']
        name = data[args['id']]['name']
        return UserType(id=id, name=name)

    def resolve_user_filtered(self, args, context, info):
        id = args['id']
        name = data[args['id']]['name']
        return UserType(id=id, name=name)

    def resolve_context(self, args, context, info):
        return context

    def resolve_error(self, args, context, info):
        raise Exception('E1')


schema = graphene.Schema(query=Query, subscription=Subscription)

pubsub = RedisPubsub()


def user_filtered_func(**kwargs):
    args = kwargs.get('args')
    return {
        'userFiltered': {
            'filter': lambda root, ctx: root.get('id') == args.get('id')
        }
    }


setup_funcs = {'user_filtered': user_filtered_func}

sub_mgr = SubscriptionManager(schema, pubsub, setup_funcs)


class PickableMock(object):
    def __init__(self, return_value=None, side_effect=None, name=None):
        self._return_value = return_value
        self._side_effect = side_effect
        self.name = name
        self.called = False
        self.call_count = 0
        self.call_args = set()

    def __call__(mock_self, *args, **kwargs):
        mock_self.called = True
        mock_self.call_count += 1
        call_args = {repr(arg) for arg in args}
        call_kwargs = {repr(item) for item in kwargs}
        mock_self.call_args = call_args | call_kwargs | mock_self.call_args
        if mock_self._side_effect and mock_self._return_value:
            mock_self._side_effect(mock_self, *args, **kwargs)
            return mock_self._return_value
        elif mock_self._side_effect:
            return mock_self._side_effect(mock_self, *args, **kwargs)
        elif mock_self._return_value:
            return mock_self._return_value

    def assert_called_once(self):
        assert self.call_count == 1

    def assert_called_with(self, *args, **kwargs):
        call_args = {repr(json.loads(json.dumps(arg))) for arg in args}
        call_kwargs = {repr(json.loads(json.dumps(item))) for item in kwargs}
        all_call_args = call_args | call_kwargs
        assert all_call_args.issubset(self.call_args)


def promisify(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        def executor(resolve, reject):
            return resolve(f(*args, **kwargs))

        return Promise(executor)

    return wrapper


def context_handler():
    raise Exception('bad')


def on_subscribe(msg, params, websocket):
    new_params = copy.deepcopy(params)
    new_params.update({'context': context_handler})
    return new_params


on_sub_handler = {'on_subscribe': promisify(on_subscribe)}

# def on_subscribe(self, msg, params, websocket):
# new_params = copy.deepcopy(params)
# new_params.update({'context': msg.get('context', {})})
# return new_params

# def on_connect(self, message, websocket):
# pass

# def on_disconnect(self, websocket):
# pass

# def on_unsubscribe(self, websocket):
# pass

# events_options = {
# 'on_subscribe':
# PickableMock(side_effect=promisify(on_subscribe), name='on_subscribe'),
# 'on_unsubscribe':
# PickableMock(side_effect=on_unsubscribe, name='on_unsubscribe'),
# 'on_connect':
# PickableMock(
# return_value={'test': 'test_context'},
# side_effect=on_connect,
# name='on_connect'),
# 'on_disconnect':
# PickableMock(side_effect=on_disconnect, name='on_disconnect')
# }


def create_app(sub_mgr, schema, options):
    app = Flask(__name__)
    sockets = Sockets(app)

    app.app_protocol = lambda environ_path_info: 'graphql-subscriptions'

    app.add_url_rule(
        '/graphql',
        view_func=GraphQLView.as_view('graphql', schema=schema, graphiql=True))

    @app.route('/publish', methods=['POST'])
    def sub_mgr_publish():
        sub_mgr.publish(*request.get_json())
        return jsonify(request.get_json())

    @sockets.route('/socket')
    def socket_channel(websocket):
        subscription_server = SubscriptionServer(sub_mgr, websocket, **options)
        subscription_server.handle()
        return []

    return app


if __name__ == "__main__":
    app = create_app(sub_mgr, schema, on_sub_handler)
    server = WebSocketServer(('', TEST_PORT), app)
    print('  Serving at host 0.0.0.0:5000...\n')
    server.serve_forever()
