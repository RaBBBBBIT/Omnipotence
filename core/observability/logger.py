import logging, sys, json, time, contextvars
from typing import Any, Dict

_request_id = contextvars.ContextVar("request_id", default="-")
_task_id    = contextvars.ContextVar("task_id", default="-")
_step       = contextvars.ContextVar("step", default="-")
_env        = "dev"   # 可从环境变量注入
_service    = "omnipotence-core"
_version    = "0.1.0"

class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: Dict[str, Any] = {
            "ts": int(time.time()*1000),
            "level": record.levelname,
            "msg": record.getMessage(),
            "logger": record.name,
            "service": _service,
            "version": _version,
            "env": _env,
            "request_id": _request_id.get(),
            "task_id": _task_id.get(),
            "step": _step.get(),
        }
        # 合并额外字段
        if hasattr(record, "extra") and isinstance(record.extra, dict):
            payload.update(record.extra)
        # 异常栈
        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)

def get_logger(name: str = "app") -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JsonFormatter())
        logger.addHandler(handler)
        logger.propagate = False
    return logger

# 便捷上下文：设置语境字段（request/task/step）
from contextlib import contextmanager
@contextmanager
def log_context(request_id: str = None, task_id: str = None, step: str = None):
    tokens = []
    if request_id: tokens.append((_request_id, _request_id.set(request_id)))
    if task_id:    tokens.append((_task_id, _task_id.set(task_id)))
    if step:       tokens.append((_step, _step.set(step)))
    try:
        yield
    finally:
        for var, tok in reversed(tokens):
            var.reset(tok)
