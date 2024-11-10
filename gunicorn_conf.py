worker = 2
worker_class = 'eventlet'
bind = '0.0.0.0:8000'
pidfile = '/tmp/gunicorn.pid'
accesslog = '/var/logs/gunicorn_bbs_access.log'
errorlog = '/var/logs/gunicorn_bbs_error.log'
capture_output = True
worker_connections = 1000
