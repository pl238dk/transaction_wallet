print(__name__)
from flask import Flask

#from application.frameworks import *
from application.frameworks import database

def init_app():
    app = Flask(__name__, instance_relative_config=False)
    
    with app.app_context():
        from .home import home
        from .api import api
        from .account import account
        from .historical import historical
        #from .{name} import {name}
        
        app.register_blueprint(home.bp_home)
        app.register_blueprint(api.bp_api)
        app.register_blueprint(account.bp_account)
        app.register_blueprint(historical.bp_historical)
        #app.register_blueprint({name}.bp_{name})
        
    return app