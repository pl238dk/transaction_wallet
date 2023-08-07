print(__name__)
from application.app import init_app

app = init_app()

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=5001)
elif __name__ != '__main__':
	import logging
	glog = logging.getLogger('gunicorn.error')
	app.logger.handlers = glog.handlers
	app.logger.setLevel(logging.DEBUG)