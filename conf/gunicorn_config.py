#import multiprocessing

# bind = "localhost:8000"
bind = "unix:/run/osmhelper.sock"
workers = 12 #multiprocessing.cpu_count() * 2 + 1
access_logfile = "-"
error_logfile = "-"
worker_class = "gevent"
# timeout = 300

