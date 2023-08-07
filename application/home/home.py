print(__name__)
#from flask import current_app as app
from flask import render_template
#from flask import request
from flask import Blueprint
#from application.app import framework
from application.app import database

bp_home = Blueprint(
    'bp_home',
    __name__,
    template_folder='templates',
    static_folder='static',
    static_url_path='/home/static',
)

@bp_home.route('/')
def home():
    with database.Database() as db:
        output = db.query_table('open_contracts')
        accounts = db.query_table('accounts')
    return render_template(
        'home.html',
        transactions=output,
        accounts=accounts,
    )