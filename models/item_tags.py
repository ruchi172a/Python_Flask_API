from DB import db


class ItemsTags(db.Model):
    __tablename__ = "items_tags"

    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey("items.id"))  #foreign key for this table
    tag_id = db.Column(db.Integer, db.ForeignKey("tags.id"))#foreign key for this table
