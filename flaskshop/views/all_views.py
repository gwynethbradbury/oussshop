# coding: utf-8
"""Helper giving access to all the views."""

from __future__ import unicode_literals

# We make an exception to the usual rule of only importing modules here for
# neatness.
#
# pylint: disable=unused-import

from flaskshop.views.shop import SHOP
# from flaskshop.views.admin import ADMIN
# from flaskshop.views.admin_announcements import ADMIN_ANNOUNCEMENTS
# from flaskshop.views.admin_data import ADMIN_DATA
# from flaskshop.views.admin_photos import ADMIN_PHOTOS
# from flaskshop.views.admin_postage import ADMIN_POSTAGE
# from flaskshop.views.admin_tickets import ADMIN_TICKETS
# from flaskshop.views.admin_users import ADMIN_USERS
# from flaskshop.views.admin_vouchers import ADMIN_VOUCHERS
# from flaskshop.views.ajax import AJAX
from flaskshop.views.dashboard import DASHBOARD
# from flaskshop.views.front import FRONT
# from flaskshop.views.group_purchase import GROUP_PURCHASE
from flaskshop.views.purchase import PURCHASE
# from flaskshop.views.api import API
#