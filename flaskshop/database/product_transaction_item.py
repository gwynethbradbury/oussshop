# coding: utf-8
"""Database model for representing a product in a transaction."""

from __future__ import unicode_literals

from flaskshop.database import db
from flaskshop.database import transaction_item
#DB = db.DB
from flaskshop.app import oussshopdb as DB

class ProductTransactionItem(transaction_item.TransactionItem):
    """Model for representing a product in a transaction."""
    __tablename__ = 'product_transaction_item'
    __mapper_args__ = {'polymorphic_identity': 'Product'}
    object_id = DB.Column(DB.Integer, primary_key=True)

    object_id = DB.Column(
        DB.Integer(),
        DB.ForeignKey('transaction_item.object_id'),
        primary_key=True
    )

    is_refund = DB.Column(
        DB.Boolean,
        nullable=False,
        default=False
    )

    product_id = DB.Column(
        DB.Integer,
        DB.ForeignKey('product.object_id'),
        nullable=False
    )
    product = DB.relationship(
        'Product',
        backref=DB.backref(
            'transaction_items',
            lazy='dynamic'
        )
    )

    def __init__(self, transaction, product, is_refund=False):
        super(ProductTransactionItem, self).__init__(transaction, 'Product')

        self.product = product
        self.is_refund = is_refund

    @property
    def value(self):
        """Get the value of this transaction item."""
        if self.is_refund:
            return 0 - self.product.price
        else:
            return self.product.price

    @property
    def description(self):
        """Get a description of the transaction item."""
        return '{0}{1} Product ({2:05d})'.format(
            'Refund of ' if self.is_refund else '',
            self.product.name,
            self.product_id
        )
