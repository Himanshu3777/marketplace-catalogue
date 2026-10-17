"""Gunicorn config — tuned for Render free tier (512MB RAM).

Workers x threads = concurrent request capacity.
2 workers x 4 threads = 8 concurrent requests (was: 1).
Each worker ~120MB, so 2 workers fit safely in 512MB.
"""
import multiprocessing

bind = "0.0.0.0:10000"
workers = 2
threads = 4
worker_class = "gthread"
timeout = 60
graceful_timeout = 30
keepalive = 5
max_requests = 1000
max_requests_jitter = 100
preload_app = True
