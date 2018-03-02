import graphene
from graphene import relay
from graphene_sqlalchemy import SQLAlchemyConnectionField, SQLAlchemyObjectType
from database import db_session, User as UserModel, Post as PostModel, Message as MessageModel, Sample as SampleModel
from sqlalchemy import and_, text
import os.path
import logging
from rx import Observable, Observer
import time
import random

logging.basicConfig(filename='/var/www/flask_graphql/error_log/error_log.txt', level=logging.DEBUG, 
                    format='%(asctime)s %(levelname)s %(name)s %(message)s')
logger = logging.getLogger(__name__)



class Users(SQLAlchemyObjectType):
    class Meta:
        model = UserModel
        interfaces = (relay.Node, )

class Posts(SQLAlchemyObjectType):
    class Meta:
        model = PostModel
        interfaces = (relay.Node, )    

class Messages(SQLAlchemyObjectType):
    class Meta:
        model = MessageModel
        interfaces = (relay.Node, ) 

class Samples(SQLAlchemyObjectType):
    class Meta:
        model = SampleModel
        interfaces = (relay.Node, ) 



# Used to Create New User
class createUser(graphene.Mutation):
    class Input:
        name = graphene.String()
        email = graphene.String()
        username = graphene.String()
    ok = graphene.Boolean()
    user = graphene.Field(Users)

    @classmethod
    def mutate(cls, _, args, context, info):
        user = UserModel(name=args.get('name'), email=args.get('email'), username=args.get('username'))
        db_session.add(user)
        db_session.commit()
        ok = True
        return createUser(user=user, ok=ok)





# Used to Change Username with Email
class changeUsername(graphene.Mutation):
    class Input:
        username = graphene.String()
        email = graphene.String()

    ok = graphene.Boolean()
    user = graphene.Field(Users)

    @classmethod
    def mutate(cls, _, args, context, info):
        query = Users.get_query(context)
        email = args.get('email')
        username = args.get('username')
        user = query.filter(UserModel.email == email).first()
        user.username = username
        db_session.commit()
        ok = True

        return changeUsername(user=user, ok = ok)


class Upload(graphene.Scalar):
    def serialize(self):
        pass

class UploadFile(graphene.Mutation):
    class Input:
        file = Upload()

    ok = graphene.Boolean()

    @staticmethod
    def mutate(root, args, context, info):
        try:
            file = request.files['file']
            file.save(os.path.join('/var/www/flask_graphql/uploads', file.filename))
            return UploadFile(ok=True)
        except Exception as e:
            # logger.error(e)
            return UploadFile(ok=False)


class Query(graphene.ObjectType):
    base = graphene.String()
    node = relay.Node.Field()
    user = SQLAlchemyConnectionField(Users)
    message = SQLAlchemyConnectionField(Messages)
    find_user = graphene.Field(lambda: Users, username = graphene.String())
    find_post = graphene.Field(lambda: Posts, id = graphene.Int())
    find_message = graphene.Field(lambda: Messages, id = graphene.Int())
    all_users = SQLAlchemyConnectionField(Users)
    all_posts = SQLAlchemyConnectionField(Posts)
    # all_messages = SQLAlchemyConnectionField(Messages)
    hello = graphene.String(name=graphene.Argument(
        graphene.String, default_value='stranger'), age=graphene.Argument(graphene.Int))

    all_messages = graphene.List(Messages, like_message = graphene.String(), limit = graphene.Int())
    def resolve_all_messages(self, args, context, info):
        try:
            # logger.error(args)
            like_formatter = text('message LIKE "%{}%"'.format(args['like_message']))
            order_by = text('id ASC')
            query = Messages.get_query(info).filter(like_formatter).order_by(order_by).limit(args['limit'])  # SQLAlchemy query
            return query.all()
        except Exception as e:
            logger.error('query error')

    # all_samples = SQLAlchemyConnectionField(Samples)
    # samples = graphene.List(Samples, message = graphene.String())
    # def resolve_samples(self, args, context, info):
    #     like_formatter = 'message LIKE "%{}%"'.format(args['message'])
    #     query = Samples.get_query(info).filter(like_formatter).order_by('id ASC').limit(2)  # SQLAlchemy query
    #     return query.all()

    def resolve_find_message(self,args,context,info):
        query = Messages.get_query(context)
        message = args.get('id')
        # you can also use and_ with filter() eg: filter(and_(param1, param2)).first()
        return query.filter(MessageModel.message == message).first()


    def resolve_find_user(self,args,context,info):
        query = Users.get_query(context)
        username = args.get('username')
        # you can also use and_ with filter() eg: filter(and_(param1, param2)).first()
        return query.filter(UserModel.username == username).first()

    def resolve_find_post(self,args,context,info):
        query = Posts.get_query(context)
        post_id = args.get('id')
        # you can also use and_ with filter() eg: filter(and_(param1, param2)).first()
        return query.filter(PostModel.id == post_id).first()


# Used to Create New Post
class createPost(graphene.Mutation):
    class Input:
        description = graphene.String()
        imageUrl = graphene.String()
    
    description = graphene.String()
    imageUrl = graphene.String()
    ok = graphene.Boolean()

    @classmethod
    def mutate(cls, _, args, context, info):
        post = PostModel(description=args.get('description'), imageUrl=args.get('imageUrl'))
        db_session.add(post)
        db_session.commit()
        ok = True
        # return createPost(ok=ok)
        source.subscribe(PrintObserver())

        return createPost(ok=ok)

class MyMutations(graphene.ObjectType):
    create_user = createUser.Field()
    create_post = createPost.Field()
    change_username = changeUsername.Field()
    upload_file = UploadFile.Field()

class RandomType(graphene.ObjectType):
    seconds = graphene.Int()
    random_int = graphene.Int()



class PrintObserver(Observer):
    def on_next(self, value):
        message = SQLAlchemyConnectionField(Messages)
        print("Receivedss {0}".format(value))
        logger.error(message)
        return message

    def on_completed(self):
        message = SQLAlchemyConnectionField(Messages)
        logger.error(message)
        print("Doness!")
        return message

    def on_error(self, error):
        print("Error Occurred: {0}".format(error))


def push_five_strings(observer):
    time.sleep(2)
    observer.on_next("Alpha")
    time.sleep(3)
    observer.on_next("Beta")
    time.sleep(3)
    observer.on_next("Gamma")
    observer.on_next("Delta")
    observer.on_next("Epsilon")
    observer.on_completed()


source = Observable.create(push_five_strings)
# source =  Observable.from_(["Alpha", "Beta", "Gamma", "Delta", "Epsilon"])



# NOTES: https://github.com/graphql-python/graphql-ws/blob/master/examples/flask_gevent/schema.p
# NOTES: add a placeholder to arguments,add a placeholder in do_??? function
# NOTES: https://github.com/ReactiveX/RxPY
class Subscription(graphene.ObjectType):
    count_seconds = graphene.Float(up_to=graphene.Int())
    post = graphene.Field(lambda: Posts)



    def resolve_count_seconds(root, info, up_to=5, placeholder=''):
        try:
            letters = Observable.from_(["Alpha", "Beta", "Gamma", "Delta", "Epsilon", "Alpha", 
                "Beta", "Gamma", "Delta", "Epsilon", "Epsilon", "Alpha", "Beta", "Gamma", "Delta", "Epsilon", 
                "Epsilon", "Alpha", "Beta", "Gamma", "Delta", "Epsilon", "Epsilon", "Alpha", "Beta", "Gamma", "Delta", "Epsilon"])

            intervals = Observable.interval(3000)

            # source.subscribe(on_next=lambda value: "Received {0}".format(value),
            #          on_completed=lambda: "Done!",
            #          on_error=lambda error: "Error Occurred: {0}".format(error))

            # source = Observable.create(push_five_strings)

            # source.subscribe(PrintObserver())

            # return Observable.interval(1000)\
            #              .map(lambda i: "{0}".format(i))\
            #              .take_while(lambda i: int(i) <= 700)

            source.subscribe(PrintObserver())
            return source

            # source = Observable.from_(["Alpha", "Beta", "Gamma", "Delta", "Epsilon"])

            # source.subscribe(on_next=lambda value: "Received {0}".format(value), on_completed=lambda: "Done!", on_error=lambda error: "Error Occurred: {0}".format(error))

            # return source



            # return Observable.from_([1,2,3,4,5,6])

            # return Observable.interval(50)\
            #             .map(lambda i: "{0}".format(i))\
            #             .take_while(lambda i: int(i) <= up_to)


        except Exception as e:
            logger.error(e)




schema = graphene.Schema(query=Query, mutation=MyMutations, subscription=Subscription, types=[Users])
