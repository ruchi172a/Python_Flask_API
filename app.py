from flask import Flask
from flask_smorest import Api  # for cleaner API building and OpenAPI docs

from resources.item import blp as ItemBlueprint   #blueprint to split routes into modules
from resources.store import blp as StoreBlueprint  #Import route definitions from resources/item.py and resources/store.py, where blp (Blueprint) is defined.
import models
from resources.DB import db
import os
from resources.tag import blp as TagBlueprint
from flask_jwt_extended import JWTManager
from resources.user import blp as UserBlueprint

from flask import Flask, jsonify

from blocklist import BLOCKLIST

from flask_migrate import Migrate #database migration
#app = Flask(__name__)   #Create a Flask app instance.

#Enable automatic OpenAPI/Swagger documentation.Provide title , version,endpoints . ,  After setting this up, your documentation is available at: http://localhost:5000/swagger-ui
def create_app(db_url=None):   #create and setup flaskApp (will be used when we write testcases so better to put in function)
    app = Flask(__name__) #Create a Flask app instance.
    app.config["PROPAGATE_EXCEPTIONS"] = True
    app.config["API_TITLE"] = "Stores REST API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.3" 
    app.config["OPENAPI_URL_PREFIX"] = "/"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
    app.config[
        "OPENAPI_SWAGGER_UI_URL"
    ] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url or os.getenv("DATABASE_URL", "sqlite:///data.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)  #initialise sqlalchemy giving our app
    migrate = Migrate(app, db) #migration
    api = Api(app)

    app.config["JWT_SECRET_KEY"] = "jose"  #secret key : generate secerte key random with this :[str(secrets.SystemRandom().getrandbits(128))]
    jwt = JWTManager(app)   #instance of jwt 
    
    @jwt.additional_claims_loader  #these are used to add additional information to jwt token
    def add_claims_to_jwt(identity):
        if identity == 1:
            return {"is_admin": True}
        return {"is_admin": False}

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return (
            jsonify({"message": "The token has expired.", "error": "token_expired"}),
            401,
        )

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return (
            jsonify(
                {"message": "Signature verification failed.", "error": "invalid_token"}
            ),
            401,
        )

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return (
            jsonify(
                {
                    "description": "Request does not contain an access token.",
                    "error": "authorization_required",
                }
            ),
            401,
        )
        
    @jwt.token_in_blocklist_loader  #used for blocklist(revoke the token)
    def check_if_token_in_blocklist(jwt_header, jwt_payload):
        return jwt_payload["jti"] in BLOCKLIST


    @jwt.revoked_token_loader #used for blocklist(revoke the token)
    def revoked_token_callback(jwt_header, jwt_payload):
        return (
            jsonify(
                {"description": "The token has been revoked.", "error": "token_revoked"}
            ),
            401,
        )
    
    @jwt.needs_fresh_token_loader
    def token_not_fresh_callback(jwt_header, jwt_payload):
        return (
            jsonify(
                {
                    "description": "The token is not fresh.",
                    "error": "fresh_token_required",
                }
            ),
            401,
        )
    # with app.app_context():  #DB migrated to falsk-migrate hence not used
    #     db.create_all()
        
    api.register_blueprint(ItemBlueprint)
    api.register_blueprint(UserBlueprint)
    api.register_blueprint(StoreBlueprint)
    api.register_blueprint(TagBlueprint)
    return app

#Below code is commented Because the logic has been moved into Blueprints inside /resources folder.
    
# # stores = [
# #     {"name": "My Store", 
# #      "items": [
# #          {"name": "my item", 
# #           "price": 15.99
# #           }
# #          ]
# #      }
# #     ]
# '''
# @app.get("/store")  #this is our get endpoint .registers the route's endpoint with Flask .when it receives a request for /store, it should run the function
# def get_stores():   #function associtaed with /store endpoint
#     return {"stores": stores}  #http://127.0.0.1:5000/store : access url 
# '''
# @app.get("/store")
# def get_stores():
#     return {"stores": list(stores.values())}

# #POST method for store adding 
# '''
# @app.post("/store")  #api should support post method for accepting new store name from postman
# def create_store():
#     request_data = request.get_json()  #Retrieve the JSON content of our request-sent from postman.
#     new_store = {"name": request_data["name"], "items": []} #create dictionary with data received
#     stores.append(new_store)  #adding data to stores
#     return new_store, 201  #returning response 
# '''
# @app.post("/store")
# def create_store():
#     store_data = request.get_json()
#     if "name" not in store_data:
#         abort(
#             400,
#             message="Bad request. Ensure 'name' is included in the JSON payload.",
#         )
#     for store in stores.values():
#         if store_data["name"] == store["name"]:
#             abort(400, message=f"Store already exists.")

#     store_id = uuid.uuid4().hex
#     store = {**store_data, "id": store_id}
#     stores[store_id] = store

#     return store
# #Post method for client to add item to store -support addinf store name in url [eg: POST /store/My Store/item]
# '''
# @app.post("/store/<string:name>/item")
# def create_item(name):  #name in post method is paased to this fucntion
#     request_data = request.get_json()
#     for store in stores:
#         if store["name"] == name:   #checking if store exists in our api
#             new_item = {"name": request_data["name"], "price": request_data["price"]}
#             store["items"].append(new_item)
#             return new_item,201
#     return {"message": "Store not found"}, 404  #if store not found 

# '''
# @app.post("/item")
# def create_item():
#     item_data = request.get_json()
#     # Here not only we need to validate data exists,
#     # But also what type of data. Price should be a float,
#     # for example.
#     if (
#         "price" not in item_data
#         or "store_id" not in item_data
#         or "name" not in item_data
#     ):
#         abort(
#             400,
#             message="Bad request. Ensure 'price', 'store_id', and 'name' are included in the JSON payload.",
#         )
#     for item in items.values():
#         if (
#             item_data["name"] == item["name"]
#             and item_data["store_id"] == item["store_id"]
#         ):
#             abort(400, message=f"Item already exists.")

#     item_id = uuid.uuid4().hex
#     item = {**item_data, "id": item_id}
#     items[item_id] = item

#     return item

# # get endpoint to retrive data appending store name(only for 1 store)
# '''@app.get("/store/<string:name>")  #enter storename from postman in url
# def get_store(name):
#     for store in stores:
#         if store["name"] == name:
#             return store
#     return {"message": "Store not found"}, 404 '''
    
# @app.get("/store/<string:store_id>")
# def get_store(store_id):
#     try:
#         # Here you might also want to add the items in this store
#         # We'll do that later on in the course
#         return stores[store_id]
#     except KeyError:
#         abort(404, message="Store not found.")

# '''
# @app.get("/store/<string:store_id>")
# def get_store(store_id):
#     try:
#         # Here you might also want to add the items in this store
#         # We'll do that later on in the course
#         return stores[store_id]
#     except KeyError:
#         return {"message": "Store not found"}, 404

# '''

# @app.get("/item/<string:item_id>")
# def get_item(item_id):
#     try:
#         return items[item_id]
#     except KeyError:
#         abort(404, message="Item not found.")
    
# # get endpoint to retrive data appending store's item
# '''
# @app.get("/store/<string:name>/item")  
# def get_item_in_store(name):
#     for store in stores:
#         if store["name"] == name:
#             return {"items": store["items"]}
#     return {"message": "Store not found"}, 404
    
# '''

# #new api to get only list of items 
# @app.get("/item")
# def get_all_items():
#     return {"items": list(items.values())}


# #we use the del keyword to remove the entry from the dictionary
# @app.delete("/item/<string:item_id>")  
# def delete_item(item_id):
#     try:
#         del items[item_id]
#         return {"message": "Item deleted."}
#     except KeyError:
#         abort(404, message="Item not found.")
        
# #clients can change item name and price, but not the store that the item belongs to.
# @app.put("/item/<string:item_id>")
# def update_item(item_id):
#     item_data = request.get_json()  #get json from postman
#     # There's  more validation to do here!
#     # Like making sure price is a number, and also both items are optional
#     # You should also prevent keys that aren't 'price' or 'name' to be passed
#     # Difficult to do with an if statement...
#     if "price" not in item_data or "name" not in item_data:
#         abort(
#             400,
#             message="Bad request. Ensure 'price', and 'name' are included in the JSON payload.",
#         )
#     try:
#         item = items[item_id]
#         item |= item_data      # |= syntax is a new dictionary operator to add data to dictionary

#         return item
#     except KeyError:
#         abort(404, message="Item not found.")
        

# @app.delete("/store/<string:store_id>")
# def delete_store(store_id):
#     try:
#         del stores[store_id]
#         return {"message": "Store deleted."}
#     except KeyError:
#         abort(404, message="Store not found.")