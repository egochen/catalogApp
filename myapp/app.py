from flask import Flask
from frontend import *
import os


app = Flask(__name__)
app.secret_key = 'super_secret_key'
app.debug = True
app.PROJECT_ROOT = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
app.register_blueprint(frontend_catalog)
app.register_blueprint(frontend_category)
app.register_blueprint(frontend_endpoint)
app.register_blueprint(frontend_oauth)
