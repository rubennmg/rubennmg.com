import time
from collections import defaultdict, deque


class LoginRateLimiter:
    def __init__(self, max_attempts: int = 5, window_seconds: int = 15 * 60) -> None:
        self.max_attempts = max_attempts
        self.window_seconds = window_seconds
        self._failures: dict[str, deque[float]] = defaultdict(deque)

    def is_limited(self, key: str) -> bool:
        attempts = self._recent_attempts(key)
        return len(attempts) >= self.max_attempts

    def record_failure(self, key: str) -> None:
        attempts = self._recent_attempts(key)
        attempts.append(time.time())

    def record_success(self, key: str) -> None:
        self._failures.pop(key, None)

    def reset(self) -> None:
        self._failures.clear()

    def _recent_attempts(self, key: str) -> deque[float]:
        now = time.time()
        attempts = self._failures[key]
        while attempts and attempts[0] <= now - self.window_seconds:
            attempts.popleft()
        return attempts


login_rate_limiter = LoginRateLimiter()
