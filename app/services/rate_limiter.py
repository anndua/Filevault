import redis
from redis.exceptions import RedisError


class RateLimitExceeded(Exception):
    def __init__(self, retry_after: int):
        self.retry_after = retry_after


class RateLimiter:
    _INCREMENT_SCRIPT = """
local current = redis.call('INCR', KEYS[1])
if current == 1 then
  redis.call('EXPIRE', KEYS[1], ARGV[1])
end
return {current, redis.call('TTL', KEYS[1])}
"""

    def __init__(self, client: redis.Redis):
        self.client = client

    def consume(self, scope: str, identity: str, limit: int, window_seconds: int) -> None:
        try:
            count, ttl = self.client.eval(
                self._INCREMENT_SCRIPT,
                1,
                f"filevault:rate:{scope}:{identity}",
                window_seconds,
            )
        except RedisError as exc:
            raise RuntimeError("Rate-limiting service is unavailable") from exc
        if int(count) > limit:
            raise RateLimitExceeded(max(1, int(ttl)))
