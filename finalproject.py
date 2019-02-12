from flask import Flask, render_template, request, redirect, jsonify, url_for
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, User, CatalogItem, Category
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response, flash
import requests
import logging


app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Catalog Items Application"


# Connect to Database and create database session
engine = create_engine('sqlite:///catalog.db?check_same_thread=False')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


'''
    SECURE LOGIN BEGIN
'''


# User Helper Functions
def createUser(login_session):
    ''' Create a new user and return user id'''
    newUser = User(name=login_session['username'],
                   email=login_session['email'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    '''get user info from user id'''
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    '''get user Id number from their email address'''
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
#    return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        logging.warning("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(
                    json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    # ADD PROVIDER TO LOGIN SESSION
    login_session['provider'] = 'google'

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(data["email"])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ''' " style = "width: 300px; height: 300px;border-radius: 150px;
                    -webkit-border-radius: 150px;
                    -moz-border-radius: 150px;"> '''
    flash("you are now logged in as %s" % login_session['username'])
    logging.info("Login successful!")
    return output


# DISCONNECT - Revoke a current user's token and reset their login_session
@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user.
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        # Reset the user's sesson.
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']

        flash('Successfully disconnected.')
        return redirect(url_for('showCategories'))
    else:
        # For whatever reason, the given token was invalid.
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


'''
    SECURE LOGIN END
'''

'''
    JSON ENDPOINT BEGIN
'''


# JSON APIs to view Category Information
@app.route('/categories/JSON')
def categoriesJSON():
    categories = session.query(Category).all()
    return jsonify(categories=[r.serialize for r in categories])


# JSON APIs to view the Information of itmes under a category
@app.route('/category/<string:category_name>/<string:catalog_name>/JSON')
def categoryItemJSON(category_name, catalog_name):
    category = session.query(Category).filter_by(name=category_name).one()
    item = session.query(CatalogItem).filter_by(
                         category_id=category.id, title=catalog_name).one()
    item = item.serialize
    del item['cat_id']
    del item['id']
    return jsonify(ItemInfo=item)


# JSON APIs to view all categories Information
@app.route('/categories/items/JSON')
def allCategoriesItemsJSON():
    categories = session.query(Category).all()
    res = []
    for r in categories:
        dct = r.serialize
        category = session.query(Category).filter_by(name=dct['name']).one()
        items = session.query(CatalogItem).filter_by(
            category_id=category.id).all()
        dct['items'] = [i.serialize for i in items]
        res.append(dct)
    return jsonify(categories=[r for r in res])


'''
    JSON ENDPOINT END
'''

'''
    Category section Begin
'''


@app.route('/')
@app.route('/categories/')
def showCategories():
    ''' display all categories'''
    categories = session.query(Category).order_by(asc(Category.name))
    catalogCategory = session.query(CatalogItem, Category).filter(
        CatalogItem.category_id == Category.id).all()
    catalogCategory = sorted(catalogCategory,
                             key=lambda x: x[0].id, reverse=True)[:10]
    if 'username' not in login_session:
        return render_template('publicCategories.html',
                               categories=categories, items=catalogCategory)
    else:
        return render_template('categories.html',
                               categories=categories, items=catalogCategory)


@app.route('/category/new', methods=['GET', 'POST'])
def newCategory():
    ''' Add a new category'''
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        newCat = Category(name=request.form['name'],
                          user_id=login_session['user_id'])
        session.add(newCat)
        session.commit()
        return redirect(url_for('showCategories'))
    else:
        return render_template('newCategory.html')
#
# @app.route('/category/<string:category_name>/edit',methods=['GET', 'POST'])
# def editCategory(category_name):
#     if 'username' not in login_session:
#         return redirect('/login')
#     toEdit = session.query(Category).filter_by(name=category_name).one()
#     if request.method == 'POST':
#         if request.form['name']:
#             toEdit.name = request.form['name']
#             return redirect(url_for('showCategories'))
#     else:
#         return render_template('editCategory.html', category=toEdit)
#
# @app.route('/category/<string:category_name>/delete',methods=['GET', 'POST'])
# def deleteCategory(category_name):
#     if 'username' not in login_session:
#         return redirect('/login')
#     toDelete = session.query(Category).filter_by(name=category_name).one()
#     if request.method == 'POST':
#         session.delete(toDelete)
#         session.commit()
#         return redirect(url_for('showCategories'))
#     else:
#         return render_template('deleteCategory.html', category=toDelete)


'''
    Category section End
'''

'''
    Catalog section Begin
'''


@app.route('/category/<string:category_name>/items')
def showCatalogItems(category_name):
    '''Show all items under a category'''
    categories = session.query(Category).order_by(asc(Category.name))
    category = session.query(Category).filter_by(name=category_name).one()
    items = session.query(CatalogItem).filter_by(category_id=category.id).all()
    return render_template('catalogItems.html', items=items, category=category,
                           categories=categories)


@app.route('/category/<string:category_name>/<string:catalog_name>')
def showOneCatalogItem(category_name, catalog_name):
    '''Show detailed information about one catalog item under a category'''
    category = session.query(Category).filter_by(name=category_name).one()
    item = session.query(CatalogItem).filter_by(
                         category_id=category.id, title=catalog_name).one()
    creator = getUserInfo(item.user_id)
    if ('username' not in login_session or
            creator.id != login_session['user_id']):
        return render_template('publicOneCatalogItem.html', item=item,
                               category_name=category.name)
    else:
        return render_template('oneCatalogItem.html', item=item,
                               category_name=category.name)


@app.route('/catalogitems/new', methods=['GET', 'POST'])
def newCatalogItem():
    '''Add a new catalog item'''
    if 'username' not in login_session:
        return redirect('/login')
    categories = session.query(Category).all()
    if request.method == 'POST':
        cat_name = request.form['categorylist']
        cat_id = session.query(Category).filter_by(name=cat_name).one().id
        newItem = CatalogItem(title=request.form['title'],
                              description=request.form['description'],
                              category_id=cat_id,
                              user_id=login_session['user_id'])
        existingItems = session.query(CatalogItem).filter_by(
            category_id=newItem.category_id).all()
        existingTitles = set([item.title for item in existingItems])
        if newItem.title not in existingTitles:
            session.add(newItem)
            session.commit()
            flash('New Catalog %s Item Successfully Created' % (newItem.title))
        else:
            flash('Same item exists!')
        return redirect(url_for('showCategories'))
    else:
        return render_template('newCatalogItem.html', categories=categories)


@app.route('/category/<string:category_name>/<string:catalog_name>/edit',
           methods=['GET', 'POST'])
def editCatalogItem(category_name, catalog_name):
    '''Edit a catalog item'''
    if 'username' not in login_session:
        return redirect('/login')
    categories = session.query(Category).all()
    category = session.query(Category).filter_by(name=category_name).one()
    itemToEdit = session.query(CatalogItem).filter_by(category_id=category.id,
                                                      title=catalog_name).one()
    if login_session['user_id'] != itemToEdit.user_id:
        return """<script>function myFunction() {
            alert('You are not authorized to edit this item. Please ' +
            'create your own restaurant in order to add items.');}
            </script><body onload='myFunction()'>"""
    if request.method == 'POST':
        if request.form['title']:
            itemToEdit.title = request.form['title']
        if request.form['description']:
            itemToEdit.description = request.form['description']
        if request.form['categorylist']:
            targetCategoryName = request.form['categorylist']
            targetCategoryID = session.query(Category).filter_by(
                name=targetCategoryName).one().id
            itemToEdit.category_id = targetCategoryID

        session.add(itemToEdit)
        session.commit()
        flash('%s Successfully Updated' % (itemToEdit.title))
        return redirect(url_for('showCatalogItems',
                                category_name=category.name))
    else:
        return render_template('editCatalogItem.html', item=itemToEdit,
                               categories=categories,
                               category_name=category.name)


@app.route('/category/<string:category_name>/<string:catalog_name>/delete',
           methods=['GET', 'POST'])
def deleteCatalogItem(category_name, catalog_name):
    '''Delete a new catalog Item'''
    if 'username' not in login_session:
        return redirect('/login')
    category = session.query(Category).filter_by(name=category_name).one()
    itemToDelete = session.query(CatalogItem).filter_by(
        category_id=category.id, title=catalog_name).one()
    if login_session['user_id'] != itemToDelete.user_id:
        return """<script>function myFunction() {
            alert('You are not authorized to delete this item. You ' +
            'can only delete items that you created.');}
            </script><body onload='myFunction()'>"""

    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        flash('%s have been deleted.' % (itemToDelete.title))
        return redirect(url_for('showCatalogItems',
                        category_name=category.name))
    else:
        return render_template('deleteCatalogItem.html',
                               item=itemToDelete, category_name=category.name)


'''
    Catalog section End
'''

if __name__ == '__main__':
    # Set up the logger for debugging
    logging.basicConfig(filename='catalogApp.log', level=logging.DEBUG)
    app.secret_key = 'super_secret_key'
    # app.debug = True
    app.run(host='0.0.0.0', port=5000, threaded=False)
