# coding: utf-8
"""Database model for a user's college."""

from __future__ import unicode_literals

# from flaskshop.database import db
# DB = db.DB
from flaskshop.app import oussshopdb as DB


class Category(DB.Model):
    """Model for a products."""
    __tablename__ = 'category'
    object_id = DB.Column(DB.Integer, primary_key=True)

    name = DB.Column(
        DB.Unicode(50),
        unique=True,
        nullable=False
    )



    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Category {0}: {1}>'.format(self.object_id, self.name)


def get_static():
    """Get static instances of the College model."""
    return [
        Category('Classes')
    ]
