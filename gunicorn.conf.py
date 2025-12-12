# Gunicorn Configuration for GASsstro.com
# Production WSGI Server Configuration

import multiprocessing

# Server Socket
bind = "0.0.0.0:5000"
backlog = 2048

# Worker Processes
workers = multiprocessing.cpu_count() * 2 + 1  # Recommended formula
worker_class = "sync"
worker_connections = 1000
max_requests = 1000  # Restart workers after this many requests (prevents memory leaks)
max_requests_jitter = 50  # Add randomness to prevent all workers restarting at once
timeout = 30
keepalive = 2

# Logging
accesslog = "logs/access.log"
errorlog = "logs/error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Process Naming
proc_name = "gassstro_api"

# Server Mechanics
daemon = False  # Set to True to run as daemon
pidfile = "gunicorn.pid"
umask = 0
user = None
group = None
tmp_upload_dir = None

# SSL (uncomment for HTTPS)
# keyfile = "/path/to/ssl/key.pem"
# certfile = "/path/to/ssl/cert.pem"

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190
