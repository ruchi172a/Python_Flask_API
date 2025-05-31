import uuid  #Used to generate unique store IDs
from flask.views import MethodView  #Base class for defining class-based views.
from flask_smorest import Blueprint, abort  #Blueprint:Used to modularize routes. , abort to send error message
#from DB import stores
from resources.schemas import StoreSchema  #A schema (probably Marshmallow) that validates and serializes store data.

from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from resources.DB import db
from models import StoreModel

blp = Blueprint("stores", __name__, description="Operations on stores")  #blp is a Blueprint named "stores". ,description helps in API documentation (via OpenAPI / Swagger).


    
@blp.route("/store/<string:store_id>") #1st endpoint
@blp.response(200, StoreSchema) #returns 200 & Use the StoreSchema to serialize the response data (i.e., convert a Python dict to JSON and validate its structure).
class Store(MethodView):           #MethodView is a Flask class that allows you to define class-based views, where each HTTP method (GET, POST, PUT, DELETE, etc.) is mapped to a method in the class.This is a more organized and scalable alternative to using function-based views.
    def get(self, store_id):   #Fetches a single store by its ID.
        store = StoreModel.query.get_or_404(store_id)
        return store
        # try:
        #     return stores[store_id]
        # except KeyError:
        #     abort(404, message="Store not found.")

    def delete(self, store_id):
        store = StoreModel.query.get_or_404(store_id)
        db.session.delete(store)
        db.session.commit()
        return {"message": "Store deleted"}, 200
        #raise NotImplementedError("Deleting a store is not implemented.")  ->this is done when we donot have enough info about the api while devloping
        # try:
        #     del stores[store_id]
        #     return {"message": "Store deleted."}
        # except KeyError:
        #     abort(404, message="Store not found.")
            
@blp.route("/store",methods=["GET", "POST"])  #2nd endpoint
class StoreListView(MethodView):        #Operations on all stores
    @blp.response(200, StoreSchema(many=True))
    def get(self):
        return StoreModel.query.all()
        #return list(stores.values())

    @blp.arguments(StoreSchema)  #Validates and deserializes incoming JSON into store_data.
    @blp.response(201, StoreSchema)  #Serializes the response with 201 Created status.
    def post(self, store_data):
        store = StoreModel(**store_data)  #create store model
        try:
            db.session.add(store)  #inserting data in databse
            db.session.commit()
        except IntegrityError:  #used for duplicate error for storename
            abort(
                400,
                message="A store with that name already exists.",
            )
        except SQLAlchemyError:  #genric error message
            abort(500, message="An error occurred creating the store.")

        return store
        # for store in stores.values():
        #     if store_data["name"] == store["name"]:
        #         abort(400, message=f"Store already exists.")

        # store_id = uuid.uuid4().hex
        # store = {**store_data, "id": store_id}
        # stores[store_id] = store

        # return store
    

