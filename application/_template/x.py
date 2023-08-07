print(__name__)
#from flask import current_app as app
from flask import render_template
#from flask import request
from flask import Blueprint
#from application.app import framework

bp_x = Blueprint(
	'bp_x',
	__name__,
	template_folder='templates',
	static_folder='static',
	static_url_path='/x/static',
)

@bp_x.route('/x')
def x():
	return render_template(
		'x.html',
	)