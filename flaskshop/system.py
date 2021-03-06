# coding: utf-8
"""Body of the system to glue all the components together."""

from __future__ import unicode_literals

import datetime
import os

import flask_login as login
# from flask.ext import login
import flask_misaka as misaka
# from flask.ext import markdown
from werkzeug import exceptions
import flask
import jinja2


# from eisitirio import app
import app, sys

APP = app.APP

APP.secret_key = 'random string'
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = set(['jpeg', 'jpg', 'png', 'gif'])
APP.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# from eisitirio.permissions import all_permissions # pylint: disable=unused-import
from flaskshop.views import all_views
from flaskshop.helpers import log_manager
from flaskshop.helpers import login_manager
from flaskshop.helpers import email_manager
from flaskshop.helpers import sms_manager
from flaskshop.helpers import timed_config
from flaskshop.helpers import util


timed_config.augment_config(APP)

@APP.before_request
def check_for_maintenance():
    """Check whether the app is in maintenance mode.

    Checks for the existence of a maintenance file, and drops the app into
    maintenance mode displaying an information page only.

    Created as early as possible to ensure it is called before
    login_manager.login_user
    """
    if os.path.exists(APP.config['MAINTENANCE_FILE_PATH']):
        APP.config['MAINTENANCE_MODE'] = True
        if (
                'maintenance' not in flask.request.path and
                'static' not in flask.request.path
        ):
            return flask.redirect(flask.url_for('maintenance'))

log_manager.LogManager(APP)
email_manager.EmailManager(APP)
login_manager.LOGIN_MANAGER.init_app(APP)
misaka.Misaka(APP)
# markdown.Markdown(APP)

APP.sms_manager = sms_manager.SmsManager()

LOG = APP.log_manager.log_main

APP.register_blueprint(all_views.SHOP)
# APP.register_blueprint(all_views.ADMIN)
# APP.register_blueprint(all_views.ADMIN_ANNOUNCEMENTS)
# APP.register_blueprint(all_views.ADMIN_DATA)
# APP.register_blueprint(all_views.ADMIN_PHOTOS)
# APP.register_blueprint(all_views.ADMIN_POSTAGE)
APP.register_blueprint(all_views.ADMIN_TICKETS)
# APP.register_blueprint(all_views.ADMIN_USERS)
# APP.register_blueprint(all_views.ADMIN_VOUCHERS)
# APP.register_blueprint(all_views.AJAX)
APP.register_blueprint(all_views.DASHBOARD)
# APP.register_blueprint(all_views.FRONT)
# APP.register_blueprint(all_views.GROUP_PURCHASE)
APP.register_blueprint(all_views.PURCHASE)

@APP.route('/old')
def router():
    """Redirect the user to the appropriate homepage."""
    if not login.current_user.is_anonymous:
        return flask.redirect(flask.url_for('dashboard.dashboard_home'))
    else:
        return flask.redirect(flask.url_for('shop.home'))

@APP.route('/maintenance')
def maintenance():
    """Display the Server Maintenance page."""
    return flask.render_template('maintenance.html'), 503

@APP.route('/static/<path:filename>')
def static(filename):
    """Custom static file handler to support custom styles and static assets."""
    custom_static = os.path.join(APP.root_path, 'custom_static')

    cache_timeout = APP.get_send_file_max_age(filename)

    if os.path.exists(os.path.join(custom_static, filename)):
        return flask.send_from_directory(custom_static, filename,
                                         cache_timeout=cache_timeout)
    else:
        return flask.send_from_directory(os.path.join(APP.root_path, 'static'),
                                         filename, cache_timeout=cache_timeout)

@APP.errorhandler(exceptions.NotFound)
@APP.errorhandler(404)
def error_404(_):
    """Display the 404 Page"""
    LOG(
        'error',
        '404 not found for URL {0}, referrer {1}'.format(
            flask.request.url,
            flask.request.referrer
        )
    )
    return flask.render_template('404.html'), 404

def server_error(code, error):
    """Generic handler for displaying Server Error pages."""
    LOG(
        'error',
        '{0} server error for URL {1}, error {2}'.format(
            code,
            flask.request.url,
            error
        )
    )
    return flask.render_template('500.html'), code

#@APP.errorhandler(Exception)
@APP.errorhandler(500)
def error_500(error):
    """Display a 500 error page."""
    return server_error(500, error)


@APP.errorhandler(405)
def error_405(error):
    """Display a 405 error page."""
    return server_error(405, error)


@APP.errorhandler(400)
def error_400(error):
    """Display a 400 error page."""
    return server_error(400, error)

@APP.context_processor
def context_processor():
    """Add a number of utilities to the rendering engine."""
    def get_all(query):
        """Wrapper to transform a query object into a set of results."""
        return query.all()

    def get_ord(date):
        """Get the appropriate ordinal for a date."""
        daymod = date.day % 10
        if daymod == 1 and not (date.day==11):
            return 'st'
        elif daymod == 2:
            return 'nd'
        elif daymod == 3:
            return 'rd'
        else:
            return 'th'

    def get_plural(number):
        """Get the potentitally plural suffix for some number of objects."""
        if number == 1:
            return ''
        else:
            return 's'

    def raise_exception():
        """Raise an exception for easy access to template debugger."""
        raise Exception

    def form_value(form, field, default=None):
        """Quick way of writing an input element's value attribute."""
        if field in form:
            return jinja2.Markup('value="{0}" '.format(form[field]))
        elif default is not None:
            return jinja2.Markup('value="{0}" '.format(default))
        else:
            return ''

    def form_selected(form, field, value):
        """Quick way of writing an input element's selected attribute."""
        if field in form and form[field] == str(value):
            return jinja2.Markup('selected="selected" ')
        else:
            return ''

    def form_checked(form, field, value):
        """Quick way of writing an input element's checked attribute."""
        if field in form and form[field] == str(value):
            return jinja2.Markup('checked="checked" ')
        else:
            return ''

    return dict(
        get_all=get_all,
        get_ord=get_ord,
        get_plural=get_plural,
        raise_exception=raise_exception,
        form_value=form_value,
        form_selected=form_selected,
        form_checked=form_checked,
        template_config={
            key: APP.config[key]
            for key in APP.config['TEMPLATE_CONFIG_KEYS']
        },
        current_year=datetime.datetime.utcnow().year,
        format_timedelta=util.format_timedelta
    )


def main():
    # app.eisitiriodb.create_all()
    APP.run(debug=True,port=5001)


if __name__ == '__main__':
    main()
