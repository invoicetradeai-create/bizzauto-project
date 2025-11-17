import redis
from rq import Queue

# Default Redis connection
# Make sure your Redis server is running on this host and port.
# You can change these values if your Redis server is configured differently.
redis_conn = redis.Redis(host='localhost', port=6379, db=0)

# Create a default queue
# You can create multiple queues for different types of jobs
queue = Queue('default', connection=redis_conn)
