from DB import db

class StoreModel(db.Model):
    __tablename__ = "stores"  #Table store and it's columns

    id = db.Column(db.Integer, primary_key=True)  #this should be same as that of item table
    name = db.Column(db.String(80), unique=True, nullable=False)
    
    items = db.relationship("ItemModel", back_populates="store", lazy="dynamic", cascade="all, delete")  #cascade used when store gets deleted item associate with it should also get deleted hence we have define that in relationship
    
    tags = db.relationship("TagModel", back_populates="store", lazy="dynamic") #store and tag table relationship