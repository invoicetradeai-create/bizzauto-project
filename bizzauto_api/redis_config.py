import os
import redis
from rq import Queue

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

redis_conn = redis.from_url(REDIS_URL, decode_responses=True)

# Create a default queue
# You can create multiple queues for different types of jobs
queue = Queue('default', connection=redis_conn)
