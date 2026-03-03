from prometheus_client import Counter, Histogram

REQUEST_COUNT = Counter("ap_civic_http_requests_total", "Total HTTP requests", ["method", "path", "status"])
REQUEST_LATENCY = Histogram("ap_civic_http_request_latency_seconds", "HTTP request latency", ["method", "path"])
CRAWL_RUN_COUNT = Counter("ap_civic_crawl_runs_total", "Total crawl runs", ["status"])

