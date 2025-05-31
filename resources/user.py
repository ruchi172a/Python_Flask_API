from flask.views import MethodView
from flask_smorest import Blueprint, abort
from passlib.hash import pbkdf2_sha256  #used to hashing password (hashing algorithm) , IF user enters 123  from postman in password ,we will has it and save it in our database

from DB import db
from models import UserModel
from schemas import UserSchema

from flask_jwt_extended import create_access_token ,get_jwt,jwt_required , create_refresh_token,get_jwt_identity
from blocklist import BLOCKLIST

blp = Blueprint("Users", "users", description="Operations on users")

@blp.route("/logout")  #concept for blocklist , created another API for adding token into jti. Once token is added here we cannot use again
class UserLogout(MethodView):
    @jwt_required()
    def post(self):
        jti = get_jwt()["jti"] 
        BLOCKLIST.add(jti)  #adding jti to blocklist
        return {"message": "Successfully logged out"}, 200

@blp.route("/register")
class UserRegister(MethodView):
    @blp.arguments(UserSchema)  # (username and pwd :as mention in schema.py)
    def post(self, user_data): #user_data : data entered by user
        if UserModel.query.filter(UserModel.username == user_data["username"]).first(): #username should be unique
            abort(409, message="A user with that username already exists.")

        user = UserModel(     #create usermodel with details given by customer
            username=user_data["username"],
            password=pbkdf2_sha256.hash(user_data["password"]),  #hashing the password while saving in db
        )
        db.session.add(user)
        db.session.commit()

        return {"message": "User created successfully."}, 201
    
@blp.route("/user/<int:user_id>")
class User(MethodView):
    """
    This resource can be useful when testing our Flask app.
    We may not want to expose it to public users, but for the
    sake of demonstration in this course, it can be useful
    when we are manipulating data regarding the users.
    """

    @blp.response(200, UserSchema)
    def get(self, user_id):
        user = UserModel.query.get_or_404(user_id)
        return user

    def delete(self, user_id):
        user = UserModel.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        return {"message": "User deleted."}, 200
    
@blp.route("/refresh")  #for refesh
class TokenRefresh(MethodView):
    @jwt_required(refresh=True) #required refresh token in authorization
    def post(self):
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user, fresh=False)
        # Make it clear that when to add the refresh token to the blocklist will depend on the app design
        jti = get_jwt()["jti"]
        BLOCKLIST.add(jti)
        return {"access_token": new_token}, 200

@blp.route("/login")  #once user loggedit . then it will hit login api with same username and password used earlier with register API. if matches then we return access token
class UserLogin(MethodView):
    @blp.arguments(UserSchema)
    def post(self, user_data):
        user = UserModel.query.filter(   #check if username and pwd is correct
            UserModel.username == user_data["username"]
        ).first()

        if user and pbkdf2_sha256.verify(user_data["password"], user.password): #verify both paasword are same
            access_token = create_access_token(identity=str(user.id), fresh=True) #creating access token
            refresh_token = create_refresh_token(user.id) #creating refresh token
            return {"access_token": access_token, "refresh_token": refresh_token}, 200


        abort(401, message="Invalid credentials.")
        
