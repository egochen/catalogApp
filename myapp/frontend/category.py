from flask import Flask, render_template, request, redirect, jsonify, url_for
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
from flask import make_response, flash, Blueprint
import requests
from myapp.models import session, User, CatalogItem, Category
from myapp.utils import createUser, getUserInfo, getUserID


frontend_category = Blueprint('frontend_category', __name__)


'''
    Category section Begin
'''


@frontend_category.route('/')
@frontend_category.route('/categories/')
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


@frontend_category.route('/category/new', methods=['GET', 'POST'])
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
# @frontend_category.route('/category/<string:category_name>/edit',methods=['GET', 'POST'])
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
# @frontend_category.route('/category/<string:category_name>/delete',methods=['GET', 'POST'])
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
