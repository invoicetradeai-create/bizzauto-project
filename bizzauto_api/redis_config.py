import redis
import os
from rq import Queue

redis_conn = redis.from_url(os.environ.get("REDIS_URL", "redis://localhost:6379/0"), decode_responses=True)

# Create a default queue
# You can create multiple queues for different types of jobs
queue = Queue('default', connection=redis_conn)
