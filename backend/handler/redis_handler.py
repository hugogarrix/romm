import sys
from enum import Enum

from config import REDIS_HOST, REDIS_PORT, REDIS_PASSWORD
from logger.logger import log
from redis import Redis
from fakeredis import FakeStrictRedis
from rq import Queue


class QueuePrio(Enum):
    HIGH = "high"
    DEFAULT = "default"
    LOW = "low"


redis_client = Redis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD, db=0)
redis_url = f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}" if REDIS_PASSWORD else f"redis://{REDIS_HOST}:{REDIS_PORT}"

high_prio_queue = Queue(name=QueuePrio.HIGH.value, connection=redis_client)
default_queue = Queue(name=QueuePrio.DEFAULT.value, connection=redis_client)
low_prio_queue = Queue(name=QueuePrio.LOW.value, connection=redis_client)

if "pytest" in sys.modules:
    cache = FakeStrictRedis(version=7)
else:
    log.info(f"Connecting to redis in {sys.argv[0]}...")
    # A seperate client that auto-decodes responses is needed
    cache = Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        password=REDIS_PASSWORD,
        db=0,
        decode_responses=True,
    )
    log.info(f"Redis connection established in {sys.argv[0]}!")
