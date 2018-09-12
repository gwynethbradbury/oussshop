# coding: utf-8
"""Helper module giving direct access to all the database models.

Because the modules containing the definition of each model are named for the
model, importing them tends to introduce name conflicts between the module and
variables/parameters containing instances of the model.

To avoid this, this module provides a quick way to access all the models with a
name that is less likely to conflict.
"""

from __future__ import unicode_literals

# We make an exception to the usual rule of only importing modules here for
# neatness.
#
# pylint: disable=unused-import

# from flaskshop.database.admin_fee import AdminFee
# from flaskshop.database.admin_fee_transaction_item import AdminFeeTransactionItem
from flaskshop.database.affiliation import Affiliation
# from flaskshop.database.announcement import Announcement
# from flaskshop.database.battels import Battels
# from flaskshop.database.battels_transaction import BattelsTransaction
# from flaskshop.database.card_transaction import CardTransaction
from flaskshop.database.paypal_transaction import PayPalTransaction
from flaskshop.database.college import College
# from flaskshop.database.dietary_requirements import DietaryRequirements
# from flaskshop.database.eway_transaction import EwayTransaction
# from flaskshop.database.group_purchase_request import GroupPurchaseRequest
# from flaskshop.database.generic_transaction_item import GenericTransactionItem
from flaskshop.database.log import Log
from flaskshop.database.photo import Photo
# from flaskshop.database.postage import Postage
# from flaskshop.database.postage_transaction_item import PostageTransactionItem
# from flaskshop.database.purchase_group import PurchaseGroup
# from flaskshop.database.statistic import Statistic
# from flaskshop.database.ticket import Ticket
from flaskshop.database.membership import Membership
from flaskshop.database.product_transaction_item import ProductTransactionItem
from flaskshop.database.transaction import DummyTransaction
from flaskshop.database.transaction import FreeTransaction
from flaskshop.database.transaction import Transaction
from flaskshop.database.transaction_item import TransactionItem
from flaskshop.database.user import User
# from flaskshop.database.voucher import Voucher
# from flaskshop.database.waiting import Waiting
# from flaskshop.database.roundup_donation import RoundupDonation
from flaskshop.database.products import Product
from flaskshop.database.category import Category
from flaskshop.database.cart import Cart
