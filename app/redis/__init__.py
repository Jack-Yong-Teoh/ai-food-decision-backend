# pylint: disable-all
from redis import Redis, ConnectionPool
from redis.asyncio import Redis as AsyncRedis
from redis.asyncio.connection import ConnectionPool as AsyncConnectionPool
from app.utilities.config import CONFIG

connection_pool = ConnectionPool(
    host=CONFIG.REDIS.HOST,
    password=CONFIG.REDIS.PASSWORD,
    port=CONFIG.REDIS.PORT,
    decode_responses=True,
    socket_keepalive=True,
    health_check_interval=30,
)
redis = Redis(connection_pool=connection_pool)

async_connection_pool = AsyncConnectionPool(
    host=CONFIG.REDIS.HOST,
    password=CONFIG.REDIS.PASSWORD,
    port=CONFIG.REDIS.PORT,
    decode_responses=True,
    socket_keepalive=True,
    health_check_interval=30,
)
async_redis = AsyncRedis(connection_pool=async_connection_pool)
