import os
from rq import SimpleWorker, Queue
from redis_config import redis_conn
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Before running the worker, ensure you have the ocr_tasks.py file with the
# process_invoice_image_gcp function created.
# You also need to have a Redis server running.
# To start the worker, run this command from your terminal in the bizzauto_api directory:
# python worker.py

# Import the function that will be executed by the worker
from ocr_tasks import process_invoice_image_gcp

listen = ['default']

if __name__ == '__main__':
    # Create a list of Queue objects, each with the redis_conn
    queues = [Queue(name, connection=redis_conn) for name in listen]
    
    # Use SimpleWorker for Windows compatibility, as it doesn't use os.fork()
    worker = SimpleWorker(queues, connection=redis_conn)
    worker.work()

print("Worker started...")