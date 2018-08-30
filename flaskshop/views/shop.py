# coding: utf-8
"""Views related to users who aren't logged in."""

from __future__ import unicode_literals

import datetime

import flask_login as login
# from flask.ext import login
import flask

from flaskshop import app
from flaskshop.database import db
from flaskshop.database import models
from flaskshop.helpers import photos
from flaskshop.helpers import util
from flaskshop.logic import affiliation_logic

# APP = app.APP#DB = db.DB
APP = flask.current_app
from flaskshop.app import oussshopdb as DB

SHOP = flask.Blueprint('shop', __name__)




from flask import *
import pymysql, hashlib, os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'random string'
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = set(['jpeg', 'jpg', 'png', 'gif'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def getLoginDetails():
    with pymysql.connect(user='root',passwd='GTG24DDa',host='localhost',db='flaskshop') as conn:
        #conn = conn.cursor()
        if 'email' not in session:
            loggedIn = False
            firstName = ''
            noOfItems = 0
        else:
            loggedIn = True
            conn.execute("SELECT userId, firstName FROM users WHERE email = '" + session['email'] + "'")
            userId, firstName = conn.fetchone()
            conn.execute("SELECT count(productId) FROM kart WHERE userId = " + str(userId))
            noOfItems = conn.fetchone()[0]
    conn.close()
    return (loggedIn, firstName, noOfItems)

# @SHOP.route("/")
# def root():
#     loggedIn, firstName, noOfItems = getLoginDetails()
#     with pymysql.connect(user='root',passwd='GTG24DDa',host='localhost',db='flaskshop') as conn:
#         #conn = conn.cursor()
#         conn.execute('SELECT productId, name, price, description, image, stock FROM products')
#         itemData = conn.fetchall()
#         conn.execute('SELECT categoryId, name FROM categories')
#         categoryData = conn.fetchall()
#     itemData = parse(itemData)
#     return render_template('shop/home.html', itemData=itemData, loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems, categoryData=categoryData)

@SHOP.route("/add")
def admin():
    with pymysql.connect(user='root',passwd='GTG24DDa',host='localhost',db='flaskshop') as conn:
        #conn = conn.cursor()
        conn.execute("SELECT categoryId, name FROM categories")
        categories = conn.fetchall()
    conn.close()
    return render_template('shop/add.html', categories=categories)

@SHOP.route("/addItem", methods=["GET", "POST"])
def addItem():
    if request.method == "POST":
        name = request.form['name']
        price = float(request.form['price'])
        description = request.form['description']
        stock = int(request.form['stock'])
        categoryId = int(request.form['category'])

        #Uploading image procedure
        image = request.files['image']
        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        imagename = filename
        with pymysql.connect(user='root',passwd='GTG24DDa',host='localhost',db='flaskshop') as conn:
            try:
                #conn = conn.cursor()
                conn.execute('''INSERT INTO products (name, price, description, image, stock, categoryId) VALUES (?, ?, ?, ?, ?, ?)''', (name, price, description, imagename, stock, categoryId))
                conn.commit()
                msg="added successfully"
            except:
                msg="error occured"
                conn.rollback()
        conn.close()
        print(msg)
        return redirect(url_for('root'))

@SHOP.route("/remove")
def remove():
    with pymysql.connect(user='root',passwd='GTG24DDa',host='localhost',db='flaskshop') as conn:
        #conn = conn.cursor()
        conn.execute('SELECT productId, name, price, description, image, stock FROM products')
        data = conn.fetchall()
    conn.close()
    return render_template('shop/remove.html', data=data)

@SHOP.route("/removeItem")
def removeItem():
    productId = request.args.get('productId')
    with pymysql.connect(user='root',passwd='GTG24DDa',host='localhost',db='flaskshop') as conn:
        try:
            #conn = conn.cursor()
            conn.execute('DELETE FROM products WHERE productID = ' + productId)
            conn.commit()
            msg = "Deleted successsfully"
        except:
            conn.rollback()
            msg = "Error occured"
    conn.close()
    print(msg)
    return redirect(url_for('root'))

@SHOP.route("/displayCategory")
def displayCategory():
        loggedIn, firstName, noOfItems = getLoginDetails()
        categoryId = request.args.get("categoryId")
        with pymysql.connect(user='root',passwd='GTG24DDa',host='localhost',db='flaskshop') as conn:
            #conn = conn.cursor()
            conn.execute("SELECT products.productId, products.name, products.price, products.image, categories.name FROM products, categories WHERE products.categoryId = categories.categoryId AND categories.categoryId = " + categoryId)
            data = conn.fetchall()
        conn.close()
        categoryName = data[0][4]
        data = parse(data)
        return render_template('shop/displayCategory.html', data=data, loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems, categoryName=categoryName)

@SHOP.route("/account/profile")
def profileHome():
    if 'email' not in session:
        return redirect(url_for('root'))
    loggedIn, firstName, noOfItems = getLoginDetails()
    return render_template("shop/profileHome.html", loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems)

@SHOP.route("/account/profile/edit")
def editProfile():
    if 'email' not in session:
        return redirect(url_for('root'))
    loggedIn, firstName, noOfItems = getLoginDetails()
    with pymysql.connect(user='root',passwd='GTG24DDa',host='localhost',db='flaskshop') as conn:
        #conn = conn.cursor()
        conn.execute("SELECT userId, email, firstName, lastName, address1, address2, zipcode, city, state, country, phone FROM users WHERE email = '" + session['email'] + "'")
        profileData = conn.fetchone()
    conn.close()
    return render_template("shop/editProfile.html", profileData=profileData, loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems)

@SHOP.route("/account/profile/changePassword", methods=["GET", "POST"])
def changePassword():
    if 'email' not in session:
        return redirect(url_for('loginForm'))
    if request.method == "POST":
        oldPassword = request.form['oldpassword']
        oldPassword = hashlib.md5(oldPassword.encode()).hexdigest()
        newPassword = request.form['newpassword']
        newPassword = hashlib.md5(newPassword.encode()).hexdigest()
        with pymysql.connect(user='root',passwd='GTG24DDa',host='localhost',db='flaskshop') as conn:
            #conn = conn.cursor()
            conn.execute("SELECT userId, password FROM users WHERE email = '" + session['email'] + "'")
            userId, password = conn.fetchone()
            if (password == oldPassword):
                try:
                    conn.execute("UPDATE users SET password = ? WHERE userId = ?", (newPassword, userId))
                    conn.commit()
                    msg="Changed successfully"
                except:
                    conn.rollback()
                    msg = "Failed"
                return render_template("changePassword.html", msg=msg)
            else:
                msg = "Wrong password"
        conn.close()
        return render_template("shop/changePassword.html", msg=msg)
    else:
        return render_template("shop/changePassword.html")

@SHOP.route("/updateProfile", methods=["GET", "POST"])
def updateProfile():
    if request.method == 'POST':
        email = request.form['email']
        firstName = request.form['firstName']
        lastName = request.form['lastName']
        address1 = request.form['address1']
        address2 = request.form['address2']
        zipcode = request.form['zipcode']
        city = request.form['city']
        state = request.form['state']
        country = request.form['country']
        phone = request.form['phone']
        with pymysql.connect(user='root',passwd='GTG24DDa',host='localhost',db='flaskshop') as con:
                try:
                    conn = con.cursor()
                    conn.execute('UPDATE users SET firstName = ?, lastName = ?, address1 = ?, address2 = ?, zipcode = ?, city = ?, state = ?, country = ?, phone = ? WHERE email = ?', (firstName, lastName, address1, address2, zipcode, city, state, country, phone, email))

                    con.commit()
                    msg = "Saved Successfully"
                except:
                    #con.rollback()
                    msg = "Error occured"
        con.close()
        return redirect(url_for('editProfile'))

# @SHOP.route("/loginForm")
# def loginForm():
#     if 'email' in session:
#         return redirect(url_for('root'))
#     else:
#         return render_template('shop/login.html', error='')

# @SHOP.route("/login", methods = ['POST', 'GET'])
# def login():
#     if request.method == 'POST':
#         email = request.form['email']
#         password = request.form['password']
#         if True:#is_valid(email, password):
#             session['email'] = email
#             return redirect(url_for('root'))
#         else:
#             error = 'Invalid UserId / Password'
#             return render_template('shop/login.html', error=error)

@SHOP.route("/productDescription")
def productDescription():
    loggedIn, firstName, noOfItems = getLoginDetails()
    productId = request.args.get('productId')
    with pymysql.connect(user='root',passwd='GTG24DDa',host='localhost',db='flaskshop') as conn:
        #conn = conn.cursor()
        conn.execute('SELECT productId, name, price, description, image, stock FROM products WHERE productId = ' + productId)
        productData = conn.fetchone()
    conn.close()
    return render_template("shop/productDescription.html", data=productData, loggedIn = loggedIn, firstName = firstName, noOfItems = noOfItems)

@SHOP.route("/addToCart")
def addToCart():
    if 'email' not in session:
        return redirect(url_for('loginForm'))
    else:
        productId = int(request.args.get('productId'))
        with pymysql.connect(user='root',passwd='GTG24DDa',host='localhost',db='flaskshop') as conn:
            #conn = conn.cursor()
            conn.execute("SELECT userId FROM users WHERE email = '" + session['email'] + "'")
            userId = conn.fetchone()[0]
            try:
                conn.execute("INSERT INTO kart (userId, productId) VALUES (?, ?)", (userId, productId))
                conn.commit()
                msg = "Added successfully"
            except:
                conn.rollback()
                msg = "Error occured"
        conn.close()
        return redirect(url_for('root'))

@SHOP.route("/cart")
def cart():
    if 'email' not in session:
        return redirect(url_for('loginForm'))
    loggedIn, firstName, noOfItems = getLoginDetails()
    email = session['email']
    with pymysql.connect(user='root',passwd='GTG24DDa',host='localhost',db='flaskshop') as conn:
        #conn = conn.cursor()
        conn.execute("SELECT userId FROM users WHERE email = '" + email + "'")
        userId = conn.fetchone()[0]
        conn.execute("SELECT products.productId, products.name, products.price, products.image FROM products, kart WHERE products.productId = kart.productId AND kart.userId = " + str(userId))
        products = conn.fetchall()
    totalPrice = 0
    for row in products:
        totalPrice += row[2]
    return render_template("shop/cart.html", products = products, totalPrice=totalPrice, loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems)

@SHOP.route("/removeFromCart")
def removeFromCart():
    if 'email' not in session:
        return redirect(url_for('loginForm'))
    email = session['email']
    productId = int(request.args.get('productId'))
    with pymysql.connect(user='root',passwd='GTG24DDa',host='localhost',db='flaskshop') as conn:
        #conn = conn.cursor()
        conn.execute("SELECT userId FROM users WHERE email = '" + email + "'")
        userId = conn.fetchone()[0]
        try:
            conn.execute("DELETE FROM kart WHERE userId = " + str(userId) + " AND productId = " + str(productId))
            conn.commit()
            msg = "removed successfully"
        except:
            conn.rollback()
            msg = "error occured"
    conn.close()
    return redirect(url_for('root'))

# @SHOP.route("/logout")
# def logout():
#     session.pop('email', None)
#     return redirect(url_for('root'))

def is_valid(email, password):
    con = pymysql.connect(user='root',passwd='GTG24DDa',host='localhost',db='flaskshop')
    conn = con.cursor()
    conn.execute('SELECT email, password FROM users')
    data = conn.fetchall()
    for row in data:
        if row[0] == email and row[1] == hashlib.md5(password.encode()).hexdigest():
            return True
    return False

# @SHOP.route("/register", methods = ['GET', 'POST'])
# def register():
#     if request.method == 'POST':
#         #Parse form data
#         password = request.form['password']
#         email = request.form['email']
#         firstName = request.form['firstName']
#         lastName = request.form['lastName']
#         address1 = request.form['address1']
#         address2 = request.form['address2']
#         zipcode = request.form['zipcode']
#         city = request.form['city']
#         state = request.form['state']
#         country = request.form['country']
#         phone = request.form['phone']
#         print(password)
#         with pymysql.connect(user='root',passwd='GTG24DDa',host='localhost',db='flaskshop') as con:
#             try:
#                 conn = con.cursor()
#                 conn.execute('INSERT INTO users (password, email, firstName, lastName, address1, address2, zipcode, city, state, country, phone) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (hashlib.md5(password.encode()).hexdigest(), email, firstName, lastName, address1, address2, zipcode, city, state, country, phone))
#
#                 con.commit()
#
#                 msg = "Registered Successfully"
#             except:
#                 #con.rollback()
#                 msg = "Error occured"
#         con.close()
#         return render_template("shop/login.html", error=msg)

# @SHOP.route("/registerationForm")
# def registrationForm():
#     return render_template("shop/register.html")

def allowed_file(filename):
    return '.' in filename and \
            filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def parse(data):
    ans = []
    i = 0
    while i < len(data):
        curr = []
        for j in range(7):
            if i >= len(data):
                break
            curr.append(data[i])
            i += 1
        ans.append(curr)
    return ans

if __name__ == '__main__':
    app.run(debug=True)

















#
#
#
@SHOP.route('/home')
def home():
    """Display the homepage.

    Contains forms for registering and logging in.
    """
    return flask.render_template(
        'shop/home.html',
        colleges=models.College.query.all(),
        affiliations=models.Affiliation.query.all(),
        form={}
    )

import os
from flask import url_for
def get_img_urls():
    img_urls = []

    names = os.listdir(os.path.join(APP.root_path, 'static/images/gallery/'))
    for n in names:
        if n.startswith('.'):
            names.remove(n)


    return names

@SHOP.route('/')
def index():
    """Display the homepage.

    Contains forms for registering and logging in.
    """
    names = get_img_urls()

    return flask.render_template(
        'index.html',
        gallery_images = names
    )

@SHOP.route('/login', methods=['GET', 'POST'])
def do_login():
    """Process a login."""
    if flask.request.method != 'POST':
        return flask.redirect(flask.url_for('router'))

    user = models.User.get_by_email(flask.request.form['email'])

    if not user or not user.check_password(flask.request.form['password']):
        if user:
            APP.log_manager.log_event(
                'Failed login attempt - invalid password',
                user=user
            )
        else:
            APP.log_manager.log_event(
                'Failed login attempt - invalid email {0}'.format(
                    flask.request.form['email']
                )
            )

        flask.flash(
            'Could not complete log in. Invalid email or password.',
            'error'
        )
        return flask.redirect(flask.url_for('shop.home'))

    if not user.verified:
        APP.log_manager.log_event(
            'Failed login attempt - not verified',
            user=user
        )
        flask.flash(
            'Could not complete log in. Email address is not confirmed.',
            'warning'
        )
        return flask.redirect(flask.url_for('shop.home'))

    login.login_user(
        user,
        remember=(
            'remember-me' in flask.request.form and
            flask.request.form['remember-me'] == 'yes'
        )
    )

    APP.log_manager.log_event(
        'Logged in',
        user=user
    )

    flask.flash('Logged in successfully.', 'success')
    return flask.redirect(flask.request.form.get('next', False) or
                          flask.url_for('shop.home'))
                          # flask.url_for('dashboard.dashboard_home'))

@SHOP.route('/register', methods=['GET', 'POST'])
def register():
    """Process a registration.

    After registration, the user must click a link in an email sent to the
    address they registered with to confirm that it is valid.
    """
    if flask.request.method != 'POST':
        return flask.redirect(flask.url_for('router'))

    flashes = []

    if models.User.get_by_email(flask.request.form['email']) is not None:
        flask.flash(
            (
                'That email address already has an associated account. '
                'Use the links below to verify your email or reset your '
                'password.'
            ),
            'error'
        )
        return flask.redirect(flask.url_for('shop.home'))

    if (
            'password' not in flask.request.form or
            'confirm' not in flask.request.form or
            flask.request.form['password'] != flask.request.form['confirm']
    ):
        flashes.append('Passwords do not match')

    if (
            'forenames' not in flask.request.form or
            flask.request.form['forenames'] == ''
    ):
        flashes.append('Forenames cannot be blank')

    if (
            'surname' not in flask.request.form or
            flask.request.form['surname'] == ''
    ):
        flashes.append('Surname cannot be blank')

    if (
            'email' not in flask.request.form or
            flask.request.form['email'] == ''
    ):
        flashes.append('Email cannot be blank')

    if (
            'password' not in flask.request.form or
            flask.request.form['password'] == ''
    ):
        flashes.append('Password cannot be blank')
    elif len(flask.request.form['password']) < 8:
        flashes.append('Password must be at least 8 characters long')

    if (
            'phone' not in flask.request.form or
            flask.request.form['phone'] == ''
    ):
        flashes.append('Phone cannot be blank')

    # if (
    #         'college' not in flask.request.form or
    #         flask.request.form['college'] == '---'
    # ):
    #     flashes.append('Please select a college')
    #
    # if (
    #         'affiliation' not in flask.request.form or
    #         flask.request.form['affiliation'] == '---'
    # ):
    #     flashes.append('Please select an affiliation')

    if APP.config['REQUIRE_USER_PHOTO'] and (
            'photo' not in flask.request.files or
            flask.request.files['photo'].filename == ''
    ):
        flashes.append('Please upload a photo')

    if 'accept_terms' not in flask.request.form:
        flashes.append('You must accept the Terms and Conditions')

    if flashes:
        flask.flash(
            (
                'There were errors in your provided details. Please fix '
                'these and try again'
            ),
            'error'
        )
        for msg in flashes:
            flask.flash(msg, 'warning')

        return flask.render_template(
            'shop/home.html',
            form=flask.request.form,
            colleges=models.College.query.all(),
            affiliations=models.Affiliation.query.all()
        )

    if APP.config['REQUIRE_USER_PHOTO']:
        photo = photos.save_photo(flask.request.files['photo'])

        DB.session.add(photo)
        DB.session.commit()
    else:
        photo = None

    user = models.User(
        flask.request.form['email'],
        flask.request.form['password'],
        flask.request.form['forenames'],
        flask.request.form['surname'],
        flask.request.form['phone'],
        models.College.query.get_or_404(flask.request.form['college']),
        models.Affiliation.query.get_or_404(flask.request.form['affiliation']),
        photo
    )

    DB.session.add(user)
    DB.session.commit()

    APP.log_manager.log_event(
        'Registered',
        user=user
    )

#todo: reinstate
    APP.email_manager.send_template(
        flask.request.form['email'],
        'Confirm your Email Address',
        'email_confirm.email',
        name=user.forenames,
        confirmurl=flask.url_for(
            'shop.confirm_email',
            user_id=user.object_id,
            secret_key=user.secret_key,
            _external=True
        ),
        destroyurl=flask.url_for(
            'shop.destroy_account',
            user_id=user.object_id,
            secret_key=user.secret_key,
            _external=True
        )
    )

    flask.flash('Your user account has been registered', 'success')
    flask.flash(
        (
            'Before you can log in, you must confirm your email address. '
            'Please check your email for further instructions. If the message '
            'does not arrive, please check your spam/junk mail folder.'
        ),
        'info'
    )

    affiliation_logic.maybe_verify_affiliation(user)

    return flask.redirect(flask.url_for('shop.home'))

# @SHOP.route('/confirmemail/<int:user_id>/<secret_key>')
# def confirm_email(user_id, secret_key):
#     """Confirm the user's email address.
#
#     The user is sent a link to this view in an email. Visiting this view
#     confirms the validity of their email address.
#     """
#     user = models.User.query.get_or_404(user_id)
#
#     if user is not None and user.secret_key == secret_key:
#         user.secret_key = None
#         user.verified = True
#
#         # This view is used to verify the email address if an already registered
#         # user decides to change their registered email.
#         if user.new_email is not None:
#             user.email = user.new_email
#             user.new_email = None
#
#         DB.session.commit()
#
#         APP.log_manager.log_event(
#             'Confirmed email',
#             user=user
#         )
#
#         if login.current_user.is_anonymous:
#             flask.flash(
#                 'Your email address has been verified. You can now log in',
#                 'info'
#             )
#         else:
#             flask.flash('Your email address has been verified.', 'info')
#     else: ## XXX/FIXME
#         APP.log_manager.log_event(
#              'User is not none, or secret key is bad'
#         )
#     #    flask.flash(
#     #        (
#     #            'Could not confirm email address. Check that you have used '
#     #            'the correct link'
#     #        ),
#     #        'warning'
#     #    )
#
#     return flask.redirect(flask.url_for('router'))
#
# @SHOP.route('/emailconfirm', methods=['GET', 'POST'])
# def email_confirm():
#     """Retry email confirmation.
#
#     If the user somehow manages to lose the email confirmation message, they can
#     use this view to have it resent.
#     """
#     if flask.request.method == 'POST':
#         user = models.User.get_by_email(flask.request.form['email'])
#
#         if not user:
#             APP.log_manager.log_event(
#                 'Attempted email confirm for {0}'.format(
#                     flask.request.form['email']
#                 )
#             )
#
#             APP.email_manager.send_template(
#                 flask.request.form['email'],
#                 'Attempted Account Access',
#                 'email_confirm_fail.email'
#             )
#         else:
#             user.secret_key = util.generate_key(64)
#             user.secret_key_expiry = None
#
#             DB.session.commit()
#
#             APP.log_manager.log_event(
#                 'Requested email confirm',
#                 user=user
#             )
#
#             APP.email_manager.send_template(
#                 flask.request.form['email'],
#                 'Confirm your Email Address',
#                 'email_confirm.email',
#                 name=user.forenames,
#                 confirmurl=flask.url_for(
#                     'shop.confirm_email',
#                     user_id=user.object_id,
#                     secret_key=user.secret_key,
#                     _external=True
#                 ),
#                 destroyurl=flask.url_for(
#                     'shop.destroy_account',
#                     user_id=user.object_id,
#                     secret_key=user.secret_key,
#                     _external=True
#                 )
#             )
#
#         flask.flash(
#             (
#                 'An email has been sent to {0} with detailing what to do '
#                 'next. Please check your email (including your spam folder) '
#                 'and follow the instructions given'
#             ).format(
#                 flask.request.form['email']
#             ),
#             'info'
#         )
#
#         return flask.redirect(flask.url_for('shop.home'))
#     else:
#         return flask.render_template('front/email_confirm.html')
#
@SHOP.route('/terms')
def terms():
    """Display the terms and conditions."""
    return flask.render_template('shop/terms.html')

# @SHOP.route('/faqs')
# def faqs():
#     """Display the frequently asked questions."""
#     return flask.render_template('front/faqs.html')
#
# @SHOP.route('/passwordreset', methods=['GET', 'POST'])
# def password_reset():
#     """Display a form to start the password reset process.
#
#     User enters their email, and is sent an email containing a link with a
#     random key to validate their identity.
#     """
#     if flask.request.method == 'POST':
#         user = models.User.get_by_email(flask.request.form['email'])
#
#         if not user:
#             APP.log_manager.log_event(
#                 'Attempted password reset for {0}'.format(
#                     flask.request.form['email']
#                 )
#             )
#
#             APP.email_manager.send_template(
#                 flask.request.form['email'],
#                 'Attempted Account Access',
#                 'password_reset_fail.email'
#             )
#         else:
#             user.secret_key = util.generate_key(64)
#             user.secret_key_expiry = (
#                 datetime.datetime.utcnow() +
#                 datetime.timedelta(minutes=30)
#             )
#
#             DB.session.commit()
#
#             APP.log_manager.log_event(
#                 'Started password reset',
#                 user=user
#             )
#
#             APP.email_manager.send_template(
#                 flask.request.form['email'],
#                 'Confirm Password Reset',
#                 'password_reset_confirm.email',
#                 name=user.forenames,
#                 confirmurl=flask.url_for(
#                     'shop.reset_password',
#                     user_id=user.object_id,
#                     secret_key=user.secret_key,
#                     _external=True
#                 )
#             )
#
#         flask.flash(
#             (
#                 'An email has been sent to {0} with detailing what to do '
#                 'next. Please check your email (including your spam folder) '
#                 'and follow the instructions given'
#             ).format(
#                 flask.request.form['email']
#             ),
#             'info'
#         )
#
#         return flask.redirect(flask.url_for('shop.home'))
#     else:
#         return flask.render_template('front/password_reset.html')
# def member_password_create(user):
#     """
#     as above, but jsut sends the reset password email
#     """
#
#     if not user:
#         APP.log_manager.log_event(
#             'Attempted password reset for {0}'.format(
#                 flask.request.form['email']
#             )
#         )
#
#         APP.email_manager.send_template(
#             flask.request.form['email'],
#             'Attempted Account Access',
#             'password_reset_fail.email'
#         )
#     else:
#         user.secret_key = util.generate_key(64)
#         user.secret_key_expiry = (
#             datetime.datetime.utcnow() +
#             datetime.timedelta(minutes=4320)
#         )#expires in 3 days
#
#         DB.session.add(user)
#         DB.session.commit()
#
#         # APP.log_manager.log_event(
#         #     'Started password creation',
#         #     user=user
#         # )
#
#         APP.email_manager.send_template(
#             user.email,
#             'Confirm Password Reset',
#             'create_user_password.email',
#             name=user.forenames,
#             confirmurl="{}resetpassword/{}/{}".format(app.APP.config['FLASKSHOP_URL'],user.object_id,user.secret_key)
#         )
#
#
#     return True
#
# @SHOP.route('/resetpassword/<int:user_id>/<secret_key>',
#              methods=['GET', 'POST'])
# def reset_password(user_id, secret_key):
#     """Complete the password reset process.
#
#     To reset their password, the user is sent an email with a link to this view.
#     Upon clicking it, they are presented with a form to define a new password,
#     which is saved when the form is submitted (to this view)
#     """
#     user = models.User.query.get_or_404(user_id)
#
#     if user is None or user.secret_key != secret_key:
#         if user is not None:
#             user.secret_key = None
#             user.secret_key_expiry = None
#
#             DB.session.commit()
#
#         flask.flash('Could not complete password reset. Please try again',
#                     'error')
#
#         return flask.redirect(flask.url_for('shop.home'))
#
#     if flask.request.method == 'POST':
#         if flask.request.form['password'] != flask.request.form['confirm']:
#             user.secret_key = util.generate_key(64)
#             user.secret_key_expiry = (datetime.datetime.utcnow() +
#                                       datetime.timedelta(minutes=5))
#
#             DB.session.commit()
#
#             flask.flash('Passwords do not match, please try again', 'warning')
#
#             return flask.redirect(
#                 flask.url_for(
#                     'shop.reset_password',
#                     user_id=user.object_id,
#                     secret_key=user.secret_key
#                 )
#             )
#         else:
#             user.set_password(flask.request.form['password'])
#
#             user.secret_key = None
#             user.secret_key_expiry = None
#
#             DB.session.commit()
#
#             APP.log_manager.log_event(
#                 'Completed password reset',
#                 user=user
#             )
#
#             flask.flash('Your password has been reset, please log in.',
#                         'success')
#
#             return flask.redirect(flask.url_for('shop.home'))
#     else:
#         return flask.render_template(
#             'front/reset_password.html',
#             user_id=user_id,
#             secret_key=secret_key
#         )
#
# @SHOP.route('/destroyaccount/<int:user_id>/<secret_key>')
# def destroy_account(user_id, secret_key):
#     """Destroy an unverified account.
#
#     If a user is unverified (and therefore has never been able to log in), we
#     allow their account to be destroyed. This is useful if somebody tries to
#     register with an email address that isn't theirs, where the actual owner of
#     the email address can trigger the account's distruction.
#
#     If a user is verified, it gets a little too complicated to destroy their
#     account (what happens to any tickets they own?)
#     """
#     user = models.User.query.get_or_404(user_id)
#
#     if user is not None and user.secret_key == secret_key:
#         if not user.is_verified:
#             for entry in user.events:
#                 entry.action = (
#                     entry.action +
#                     ' (destroyed user with email address {0})'.format(
#                         user.email
#                     )
#                 )
#                 entry.user = None
#
#             DB.session.delete(user)
#             DB.session.delete(user.photo)
#             DB.session.commit()
#
#             photos.delete_photo(user.photo)
#
#             APP.log_manager.log_event(
#                 'Deleted account with email address {0}'.format(
#                     user.email
#                 )
#             )
#
#             flask.flash('The account has been deleted.', 'info')
#         else:
#             APP.log_manager.log_event(
#                 'Attempted deletion of verified account',
#                 user=user
#             )
#
#             flask.flash('Could not delete user account.', 'warning')
#     else:
#         flask.flash(
#             (
#                 'Could not delete user account. Check that you have used the '
#                 'correct link'
#             ),
#             'warning'
#         )
#
#     return flask.redirect(flask.url_for('shop.home'))
#
# @SHOP.route('/logout')
# @login.login_required
# def logout():
#     """Log out the currently logged in user.
#
#     The system allows admins to impersonate other users; this view checks if the
#     currently logged in user is being impersonated, and if so logs back in as
#     the admin who is impersonating them.
#     """
#     if 'actor_id' in flask.session:
#         APP.log_manager.log_event(
#             'Finished impersonating user',
#             user=login.current_user
#         )
#
#         actor = models.User.query.get_or_404(flask.session['actor_id'])
#
#         flask.session.pop('actor_id', None)
#
#         if actor:
#             login.login_user(
#                 actor
#             )
#
#             return flask.redirect(flask.url_for('admin.admin_home'))
#
#     APP.log_manager.log_event(
#         'Logged Out',
#         user=login.current_user
#     )
#
#     login.logout_user()
#     return flask.redirect(flask.url_for('shop.home'))
