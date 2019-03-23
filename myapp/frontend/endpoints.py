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


frontend_endpoint = Blueprint('frontend_endpoint', __name__)

'''
    JSON ENDPOINT BEGIN
'''

# JSON APIs to view Category Information
@frontend_endpoint.route('/categories/JSON')
def categoriesJSON():
    categories = session.query(Category).all()
    return jsonify(categories=[r.serialize for r in categories])


# JSON APIs to view the Information of itmes under a category
@frontend_endpoint.route('/category/<string:category_name>/<string:catalog_name>/JSON')
def categoryItemJSON(category_name, catalog_name):
    category = session.query(Category).filter_by(name=category_name).one()
    item = session.query(CatalogItem).filter_by(
                         category_id=category.id, title=catalog_name).one()
    item = item.serialize
    del item['cat_id']
    del item['id']
    return jsonify(ItemInfo=item)


# JSON APIs to view all categories Information
@frontend_endpoint.route('/categories/items/JSON')
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
