# coding: utf-8
"""Database model for representing an item in a transaction."""

from __future__ import unicode_literals

from flaskshop.database import db
#DB = db.DB
from flaskshop.app import oussshopdb as DB

class TransactionItem(DB.Model):
    """Model for representing an item in a transaction.

    Not used directly, use GenericTransactionItem, ProductTransactionItem,
    PostageTransactionItem, AdminFeeTransactionItem subtypes instead.
    """
    __tablename__ = 'transaction_item'
    object_id = DB.Column(DB.Integer, primary_key=True)

    item_type = DB.Column(
        DB.Enum(
            'Ticket',
            'Generic',
            'Postage',
            'AdminFee',
            'Product',
            'Membership',
        ),
        nullable=False
    )

    transaction_id = DB.Column(
        DB.Integer,
        DB.ForeignKey('transaction.object_id'),
        nullable=True
    )
    transaction = DB.relationship(
        'Transaction',
        backref=DB.backref(
            'items',
            lazy='dynamic'
        )
    )

    __mapper_args__ = {'polymorphic_on': item_type}

    def __init__(self, transaction, item_type):
        self.transaction = transaction
        self.item_type = item_type
