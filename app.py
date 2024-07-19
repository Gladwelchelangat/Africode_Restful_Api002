from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api,Resource,reqparse,abort,fields,marshal_with
from datetime import datetime,timezone

app = Flask(__name__)
api=Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] ='sqlite:///database.db'
db = SQLAlchemy(app)


class UserModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username =db.Column(db.String(20),unique=True,nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    posts= db.relationship('PostModel',backref="author", lazy=True)

    def __repr__(self):
        return  self.username
    
class PostModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False) 
    createdat=db.Column(db.DateTime,nullable=False,default=lambda:datetime.now(timezone.utc))
    user_id = db.Column(db.Integer, db.ForeignKey('user_model.id'), nullable=False)

    def __repr__(self):
        return self.title

    
app.app_context().push()
db.create_all()


    
users_args=reqparse.RequestParser()
users_args.add_argument('username', type=str, required=True, help='Username is required')
users_args.add_argument('email', type=str, required=True, help='Email is required')


userFields={
    'id': fields.Integer,
    'username': fields.String,
    'email': fields.String,

}
class Users(Resource):
    @marshal_with(userFields)
    def get(self):
        users =UserModel.query.all()
        return users,200
    @marshal_with(userFields)
    def post(self):
        args = users_args.parse_args()
        username =args['username']
        email = args['email']
        newuser=UserModel(username=username, email=email)
        db.session.add(newuser)
        db.session.commit()
        return newuser, 201
    
class User(Resource):
    @marshal_with(userFields)
    def get(self, id):
        user = UserModel.query.filter_by(id=id).first()
        if not user:
            abort(404, message=f"User with  ID {id}not found")
        return user

    @marshal_with(userFields)
    def patch(self, id):
        user = UserModel.query.filter_by(id=id).first()
        if not user:
            abort(404, message=f"User with ID {id}not found")

        args = users_args.parse_args()
        user.username = args['username']
        user.email = args['email']
        db.session.commit()
        return user, 200
    @marshal_with(userFields)
    def delete(self, id):
        user = UserModel.query.filter_by(id=id).first()
        if not user:
            abort(404, message=f"User with ID {id}not found")
        db.session.delete(user)
        db.session.commit()
        users =UserModel.query.all()
        return users, 200
    
class posts(Resource):

    def get(self):
        posts = PostModel.query.all()
        return posts,200
             
api.add_resource(posts,"/posts/")
api.add_resource(Users,"/users/") 
api.add_resource(User,"/users/<int:id>")


@app.route('/')
def home():
    return ('Hello world')

if __name__ == '__main__':
    app.run( debug=True)
 