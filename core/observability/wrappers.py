import time
from functools import wraps
from typing import Callable
from .logger import get_logger
from .metrics import REQUESTS_TOTAL, LATENCY

def instrument(component: str, action: str) -> Callable:
    """
    给函数自动记录：开始/结束日志、异常日志、成功率、延迟直方图。
    """
    log = get_logger(f"{component}.{action}")

    def decorator(fn: Callable):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            start = time.perf_counter()
            log.info("start")
            try:
                res = fn(*args, **kwargs)
                dur = time.perf_counter() - start
                LATENCY.labels(component, action).observe(dur)
                REQUESTS_TOTAL.labels(component, action, "success").inc()
                log.info("done", extra={"extra": {"latency_sec": round(dur, 4)}})
                return res
            except Exception as e:
                dur = time.perf_counter() - start
                LATENCY.labels(component, action).observe(dur)
                REQUESTS_TOTAL.labels(component, action, "error").inc()
                log.exception("failed", extra={"extra": {"latency_sec": round(dur, 4)}})
                raise
        return wrapper
    return decorator
