import multiprocessing


worker_class = 'gevent'

keepalive = 0

workers = multiprocessing.cpu_count()

bind = ['0.0.0.0:8000']
