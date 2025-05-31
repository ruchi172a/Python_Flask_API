from DB import db
class ItemModel(db.Model):
    __tablename__ = "items"  #this is the table name
 
    #columns of the table
    id = db.Column(db.Integer, primary_key=True)  #by default autoIncrement happen for next entry
    name = db.Column(db.String(80), unique=True, nullable=False)  #cannot have null values , each item should be unique
    description = db.Column(db.String)
    price = db.Column(db.Float(precision=2), unique=False, nullable=False)
    store_id = db.Column(db.Integer, unique=False, nullable=False)  #this will be link in store and item table
    
    store_id = db.Column(    #create relationship  , defining ForeignKey in item table(link store_id to id column in item)
        db.Integer, db.ForeignKey("stores.id"), unique=False, nullable=False
    )
    store = db.relationship("StoreModel", back_populates="items")  #StoreModel class
    
    tags = db.relationship("TagModel", back_populates="items", secondary="items_tags")