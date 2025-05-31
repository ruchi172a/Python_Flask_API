# import uuid
from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from resources.schemas import ItemSchema, ItemUpdateSchema
#from DB import items

from sqlalchemy.exc import SQLAlchemyError
from resources.DB import db
from models import ItemModel

from flask_jwt_extended import jwt_required ,get_jwt

blp = Blueprint("Items", __name__, description="Operations on items")


@blp.route("/item/<string:item_id>")  #define api using blueprint
class Item(MethodView):
    @jwt_required(fresh=True)  #fresh jwt token is mandate
    @blp.response(200, ItemSchema)  #main success response with status code and ItemSchema fields 
    def get(self, item_id):
        item = ItemModel.query.get_or_404(item_id)  #query comes from db.model that is given by flaskalchemy .retrives the item using primary key , if no primary key then abort with 404
        return item
        # try:
        #     return items[item_id]
        # except KeyError:
        #     abort(404, message="Item not found.")
    @jwt_required()
    def delete(self, item_id):
        
        jwt = get_jwt()         #extra information to jwt[Optional] .delete only allows for admin
        if not jwt.get("is_admin"):
            abort(401, message="Admin privilege required.")
        
        item = ItemModel.query.get_or_404(item_id)  #grabbing the store from database
        db.session.delete(item)
        db.session.commit()
        return {"message": "Item deleted."} ,200 #adding ,200 -is optional for response code we add like that
        # try:
        #     del items[item_id]
        #     return {"message": "Item deleted."}
        # except KeyError:
        #     abort(404, message="Item not found.")

    
    @blp.arguments(ItemUpdateSchema)
    @blp.response(200, ItemSchema)
    def put(self, item_data, item_id):  #getting the item and update if exists ,if not then create new item
        item = ItemModel.query.get(item_id)
        if item:                               #if exisit then update
            item.price = item_data["price"]  
            item.name = item_data["name"]
        else:                                  #if item not exist then we need item,name and stor_id to create new 
            item = ItemModel(id=item_id, **item_data)  #item_id passed in postman request

        db.session.add(item)
        db.session.commit()

        return item
        # try:
        #     item = items[item_id]

        #     # https://blog.teclado.com/python-dictionary-merge-update-operators/
        #     item |= item_data

        #     return item
        # except KeyError:
        #     abort(404, message="Item not found.")


@blp.route("/item",methods=["GET", "POST"])
class ItemList(MethodView):
    @jwt_required()
    @blp.response(200, ItemSchema(many=True))  #many items then giving likt this
    def get(self):
        # return items.values()
        return ItemModel.query.all()  #all method of query allows us to go through all items

    @jwt_required()
    @blp.arguments(ItemSchema)
    @blp.response(201, ItemSchema)
    def post(self, item_data):
        item = ItemModel(**item_data)  #pass the data to model

        try:
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An error occurred while inserting the item.")

        return item
            # for item in items.values():  //this check is already happening in db file(unique column, so removing this)
            #     if (
            #         item_data["name"] == item["name"]
            #         and item_data["store_id"] == item["store_id"]
            #     ):
            #         abort(400, message=f"Item already exists.")

            # item_id = uuid.uuid4().hex   //we will be using models hence removing this code
            # item = {**item_data, "id": item_id}
            # items[item_id] = item
            # return item
    
