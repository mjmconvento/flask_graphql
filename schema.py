import graphene
from graphene import relay
from graphene_sqlalchemy import SQLAlchemyConnectionField, SQLAlchemyObjectType
from database import db_session, User as UserModel, Post as PostModel, Message as MessageModel, Sample as SampleModel
from sqlalchemy import and_, text
import os.path
from flask import request
import logging

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
        return createPost(ok=ok)


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
            logger.error(e)
            return UploadFile(ok=False)


class Query(graphene.ObjectType):
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
            logger.error(args)
            like_formatter = text('message LIKE "%{}%"'.format(args['like_message']))
            order_by = text('id ASC')
            query = Messages.get_query(info).filter(like_formatter).order_by(order_by).limit(args['limit'])  # SQLAlchemy query
            return query.all()
        except Exception as e:
            logger.error(e)

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

class MyMutations(graphene.ObjectType):
    create_user = createUser.Field()
    create_post = createPost.Field()
    change_username = changeUsername.Field()
    upload_file = UploadFile.Field()


schema = graphene.Schema(query=Query, mutation=MyMutations, types=[Users])
