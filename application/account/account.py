print(__name__)
#from flask import current_app as app
from flask import render_template
#from flask import request
from flask import Blueprint
#from application.app import framework
from application.app import database

bp_account = Blueprint(
    'bp_account',
    __name__,
    template_folder='templates',
    static_folder='static',
    static_url_path='/account/static',
)

@bp_account.route('/account')
def account():
    with database.Database() as db:
        output = db.query_table('accounts')
    return render_template(
        'account.html',
        accounts=output,
    )