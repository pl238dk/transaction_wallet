print(__name__)
#from flask import current_app as app
from flask import render_template
#from flask import request
from flask import Blueprint
#from application.app import framework
from application.app import database

bp_historical = Blueprint(
    'bp_historical',
    __name__,
    template_folder='templates',
    static_folder='static',
    static_url_path='/historical/static',
)

@bp_historical.route('/historical')
def historical():
    with database.Database() as db:
        output = db.query_table('transactions')
        accounts = db.query_table('accounts')
    return render_template(
        'historical.html',
        transactions=output,
        accounts=accounts,
    )