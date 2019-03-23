from flask import Flask, render_template, request, redirect, jsonify, url_for
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response, flash, Blueprint
import requests
from myapp.models import session, User, CatalogItem, Category
from myapp.utils import createUser, getUserInfo, getUserID


frontend_catalog = Blueprint('frontend_catalog', __name__)

'''
    Catalog section Begin
'''

@frontend_catalog.route('/category/<string:category_name>/items')
def showCatalogItems(category_name):
    '''Show all items under a category'''
    categories = session.query(Category).order_by(asc(Category.name))
    category = session.query(Category).filter_by(name=category_name).one()
    items = session.query(CatalogItem).filter_by(category_id=category.id).all()
    return render_template('catalogItems.html', items=items, category=category,
                           categories=categories)


@frontend_catalog.route('/category/<string:category_name>/<string:catalog_name>')
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


@frontend_catalog.route('/catalogitems/new', methods=['GET', 'POST'])
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


@frontend_catalog.route('/category/<string:category_name>/<string:catalog_name>/edit',
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


@frontend_catalog.route('/category/<string:category_name>/<string:catalog_name>/delete',
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
