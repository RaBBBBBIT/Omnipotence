from prometheus_client import Counter, Histogram, start_http_server
import os

# 指标命名：<namespace>_<subsystem>_<metric>
NS = "omni"

REQUESTS_TOTAL = Counter(
    f"{NS}_actions_total",
    "Total actions processed.",
    ["component", "action", "status"]  # success|error
)

LATENCY = Histogram(
    f"{NS}_latency_seconds",
    "Action latency in seconds.",
    ["component", "action"],
    # 直方图桶：覆盖亚秒到数秒（截图+OCR ≤1s 目标）
    buckets=(0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 0.75, 1, 1.5, 2, 3, 5)
)

def serve_metrics(port: int = None):
    """在进程内暴露 /metrics（Prometheus 抓取用）"""
    port = port or int(os.getenv("METRICS_PORT", "9108"))
    start_http_server(port)
    return port
