import redis
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize the connection
# logic corresponds to the video's client creation
redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST"),
    port=int(os.getenv("REDIS_PORT")), # Cast port to int
    password=os.getenv("REDIS_PASSWORD"),
    decode_responses=True, # Essential for Python to get strings instead of bytes
    ssl=False # <--- CHANGE THIS FROM True TO False
)

def get_redis_client():
    try:
        yield redis_client
    finally:
        # Connection pool handles closing automatically usually, 
        # but explicit close can be done here if needed
        pass 