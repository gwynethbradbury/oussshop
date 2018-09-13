# coding: utf-8
"""Database model for a user's college."""

from __future__ import unicode_literals

# from flaskshop.database import db
#DB = db.DB
from flaskshop.app import oussshopdb as DB


class Product(DB.Model):
    """Model for a products."""
    __tablename__ = 'product'
    object_id = DB.Column(DB.Integer, primary_key=True)


    name = DB.Column(
        DB.Unicode(50),
        unique=True,
        nullable=False
    )

    price_ = DB.Column(
        DB.Integer(),
        nullable=False
    )

    lot_of = DB.Column(
        DB.Integer(),
        nullable=False,
        default=1
    )

    description = DB.Column(
        DB.Text(),
        nullable=False
    )

    photo_id = DB.Column(
        DB.Integer,
        DB.ForeignKey('photo.object_id'),
        nullable=True
    )
    photo = DB.relationship(
        'Photo',
        backref=DB.backref(
            'product',
            uselist=False
        )
    )
    category_id = DB.Column(
        DB.Integer,
        DB.ForeignKey('category.object_id'),
        nullable=True
    )
    category = DB.relationship(
        'Category',
        backref=DB.backref(
            'product_cat',
            uselist=False
        )
    )

    stock=1000

    def __init__(self, name, category_id,description="a thing", price=1,lot=1):
        self.name = name
        self.price = price
        self.category_id = category_id
        self.photo=None
        self.description = description
        self.lot_of=lot

    def __repr__(self):
        return '<Product {0}: {1}>'.format(self.object_id, self.name)

    @property
    def price_pounds(self):
        """Get the price of this membership as a string of pounds and pence."""
        price = '{0:03d}'.format(self.price)
        return price[:-2] + '.' + price[-2:]

    @property
    def price(self):
        """Get the price of the membership."""
        return self.price_

    @price.setter
    def price(self, value):
        """Set the price of the membership."""
        self.price_ = max(value, 0)

        if self.price_ == 0:
            self.mark_as_paid()


def get_static(category_id):
    """Get static instances of the category model."""
    return [
        Product('Classx10',category_id=category_id,description="block of 8 classes",price=3000,lot=10),
        Product('Class',category_id=category_id,description="block of 8 classes",price=400),

    ]
