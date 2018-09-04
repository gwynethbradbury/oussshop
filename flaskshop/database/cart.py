# coding: utf-8
"""Database model for a user's college."""

from __future__ import unicode_literals

# from flaskshop.database import db
#DB = db.DB
from flaskshop.app import oussshopdb as DB


class Cart(DB.Model):
    """Model for a cart."""
    __tablename__ = 'cart'
    object_id = DB.Column(DB.Integer, primary_key=True)

    user_id = DB.Column(
        DB.Integer,
        DB.ForeignKey('user.object_id'),
        nullable=True
    )
    user = DB.relationship(
        'User',
        backref=DB.backref(
            'cart',
            uselist=False
        )
    )
    product_id = DB.Column(
        DB.Integer,
        DB.ForeignKey('product.object_id'),
        nullable=True
    )
    product = DB.relationship(
        'Product',
        backref=DB.backref(
            'cart_product',
            uselist=False
        )
    )


    def __init__(self, user,product):
        self.user_id = user
        self.product_id=product

    def __repr__(self):
        return '<Products {0}: {1}>'.format('todo','todo')



