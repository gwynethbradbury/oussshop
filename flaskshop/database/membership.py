# coding: utf-8
"""Database model for memberships."""

from __future__ import unicode_literals

import datetime
import string

from sqlalchemy.ext import hybrid

# from flaskshop import app
# from flaskshop.database import db
# from flaskshop.helpers import util

import flask
APP = flask.current_app#app.APP#DB = db.DB
from flaskshop.app import oussshopdb as DB
from flaskshop.helpers import util
import pyqrcode
import io


class Membership(DB.Model):
    """Model for membership."""
    __tablename__ = 'membership'
    object_id = DB.Column(DB.Integer,primary_key=True)

    membership_type = DB.Column(
        DB.Unicode(50),
        nullable=False
    )
    owner_id = DB.Column(
        DB.Integer,
        DB.ForeignKey('user.object_id'),
        nullable=False
    )
    owner = DB.relationship(
        'User',
        backref=DB.backref(
            'memberships',
            lazy='dynamic',
            order_by=b'Membership.cancelled'
        ),
        foreign_keys=[owner_id]
    )

    paid = DB.Column(
        DB.Boolean(),
        default=False,
        nullable=False
    )
    cancelled = DB.Column(
        DB.Boolean(),
        default=False,
        nullable=False
    )
    price_ = DB.Column(
        DB.Integer(),
        nullable=False
    )
    note = DB.Column(
        DB.UnicodeText(),
        nullable=True
    )
    expires = DB.Column(
        DB.DateTime(),
        nullable=True
    )
    barcode = DB.Column(
        DB.Unicode(20),
        unique=True,
        nullable=True
    )


    def __init__(self, owner, membership_type, price):
        self.owner = owner
        self.membership_type = membership_type
        self.price = price

        y = datetime.datetime.utcnow().year
        m = datetime.datetime.utcnow().month
        if m>=10:
            y = y+1

        self.expires = datetime.datetime(y,10,1)#(datetime.datetime.utcnow()) +
                        #APP.config['MEMBERSHIP_EXPIRY_TIME'])

    def generate_barcode(self):
        # generate barcode
        key = util.generate_key(20).decode('utf-8')
        self.barcode = key


    def generate_qrcode(self):
        # generate QR
        qrcode_img = pyqrcode.create('{0}admin/membership/validate-ticket/{1}/{2}'.format(APP.config['EISITIRIO_URL'],
                                                                                      self.object_id,
                                                                                      self.barcode))
        buffer = io.BytesIO()
        qrcode_img.png(buffer, scale=20)

        f = open('/Users/Gwyneth/Documents/repositories/oussshop/flaskshop/tmp.png', 'wb')
        f.write(buffer)
        f.close()
        return buffer.getvalue()


    def __repr__(self):
        return '<Membership {0} owned by {1} ({2})>'.format(
            self.object_id,
            self.owner.full_name,
            self.owner.object_id
        )


    def can_be_cancelled(self):
        return False

    def can_be_resold(self):
        return False

    def can_be_claimed(self):
        return False

    def can_be_reclaimed(self):
        return False

    def has_holder(self):
        return False

    def can_be_paid_for(self):
        if self.paid==0:
            return True
        return False

    def can_be_collected(self):
        return False

    def is_assigned(self):
        return True


    @property
    def price_pounds(self):
        """Get the price of this membership as a string of pounds and pence."""
        price = '{0:03d}'.format(self.price)
        return price[:-2] + '.' + price[-2:]

    @property
    def transaction(self):
        """Get the transaction this membership was paid for in."""
        for transaction_item in self.transaction_items:
            if transaction_item.transaction.paid:
                return transaction_item.transaction

        return None

    @property
    def payment_method(self):
        """Get the payment method for this membership."""
        transaction = self.transaction

        if transaction:
            return transaction.payment_method
        else:
            return 'Unknown Payment Method'

    @property
    def price(self):
        """Get the price of the membership."""
        return self.price_

    @property
    def status(self):
        """Get the status of this membership."""
        if not self.paid:
            return 'Awaiting payment. Expires {0}.'.format(
                self.expires.strftime('%H:%M %d/%m/%Y')
            )
        elif APP.config['REQUIRE_USER_PHOTO']:
            if not self.holder.photo.verified:
                return 'Awaiting verification of holder photo.'
        else:
            return 'Valid membership'

    @price.setter
    def price(self, value):
        """Set the price of the membership."""
        self.price_ = max(value, 0)

        if self.price_ == 0:
            self.mark_as_paid()

    @hybrid.hybrid_property
    def collected(self):
        """Has this membership been assigned a barcode."""
        return self.barcode != None # pylint: disable=singleton-comparison

    def mark_as_paid(self):
        """Mark the membership as paid, and clear any expiry."""
        self.paid = True
        self.expires = None

    def add_note(self, note):
        """Add a note to the membership."""
        if not note.endswith('\n'):
            note = note + '\n'

        if self.note is None:
            self.note = note
        else:
            self.note = self.note + note

    @staticmethod
    def count():
        """How many memberships have been sold."""
        # TODO
        return Membership.query.filter(Membership.paid == True).count() # pylint: disable=singleton-comparison

    @staticmethod
    def write_csv_header(csv_writer):
        """Write the header of a CSV export file."""
        csv_writer.writerow([
            'Membership ID',
            'Membership Type',
            'Paid',
            'Cancelled',
            'Price (Pounds)',
            'Notes',
            'Expires',
            'Barcode',
            'Owner\' User ID',
            'Owner\'s Name',
        ])

    def write_csv_row(self, csv_writer):
        """Write this object as a row in a CSV export file."""
        csv_writer.writerow([
            self.object_id,
            self.membership_type,
            'Yes' if self.paid else 'No',
            'Yes' if self.cancelled else 'No',
            self.price_pounds,
            self.note,
            self.expires.strftime(
                '%Y-%m-%d %H:%M:%S'
            ) if self.expires is not None else 'N/A',
            self.barcode if self.barcode is not None else 'N/A',
            self.owner_id,
            self.owner.full_name.encode('utf-8'),
        ])
