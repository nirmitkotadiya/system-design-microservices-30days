# Day 19: Observability — Concepts Deep Dive

## 1. Monitoring vs. Observability

**Monitoring**: Watching known metrics and alerting when they cross thresholds.  
"CPU > 90% → alert"

**Observability**: The ability to ask arbitrary questions about your system's behavior.  
"Why is the p99 latency for user_id=123 high only on Tuesdays?"

Monitoring tells you something is wrong. Observability helps you understand why.

---

## 2. The Three Pillars of Observability

### Pillar 1: Metrics

Metrics are numerical measurements over time.

```
request_count{service="order", status="200"} = 1000
request_latency_p99{service="order"} = 245ms
error_rate{service="payment"} = 0.02
cache_hit_rate{service="user"} = 0.94
```

**Types of metrics**:
- **Counter**: Monotonically increasing (total requests, total errors)
- **Gauge**: Current value (active connections, queue depth, memory usage)
- **Histogram**: Distribution of values (request latency, response size)
- **Summary**: Pre-computed percentiles

**The Four Golden Signals** (Google SRE):
1. **Latency**: How long requests take (p50, p95, p99)
2. **Traffic**: How many requests per second
3. **Errors**: Error rate (4xx, 5xx)
4. **Saturation**: How "full" the system is (CPU %, queue depth)

**Tools**: Prometheus (collection), Grafana (visualization)

### Pillar 2: Logs

Logs are timestamped records of events.

```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "level": "ERROR",
  "service": "payment-service",
  "trace_id": "abc123",
  "span_id": "def456",
  "user_id": "user_789",
  "message": "Payment failed",
  "error": "Card declined",
  "amount": 99.99,
  "duration_ms": 234
}
```

**Structured logging** (JSON) is essential for distributed systems. You need to search and filter logs programmatically.

**Log levels**:
- `DEBUG`: Detailed diagnostic info (dev only)
- `INFO`: Normal operation events
- `WARN`: Unexpected but handled situations
- `ERROR`: Errors that need attention
- `FATAL`: System is unusable

**Tools**: ELK Stack (Elasticsearch, Logstash, Kibana), Loki + Grafana, Datadog

### Pillar 3: Distributed Traces

A trace follows a single request as it travels through multiple services.

```
User Request (trace_id: abc123)
│
├── API Gateway (span: 5ms)
│   │
│   ├── Order Service (span: 120ms)
│   │   │
│   │   ├── PostgreSQL query (span: 15ms)
│   │   │
│   │   └── Payment Service (span: 95ms)
│   │       │
│   │       └── Stripe API (span: 80ms)
│   │
│   └── Notification Service (span: 10ms)
│       │
│       └── SendGrid API (span: 8ms)
│
Total: 135ms
```

**How it works**:
1. First service generates a `trace_id`
2. Each service creates a `span` with start/end time
3. Spans are linked by `trace_id` and `parent_span_id`
4. All spans are sent to a tracing backend (Jaeger, Zipkin)

**Tools**: Jaeger, Zipkin, AWS X-Ray, Datadog APM

---

## 3. SLOs, SLAs, and Error Budgets

### SLI (Service Level Indicator)
A metric that measures service quality.
```
SLI = (successful requests) / (total requests)
SLI = (requests with latency < 200ms) / (total requests)
```

### SLO (Service Level Objective)
A target for an SLI.
```
SLO: 99.9% of requests succeed
SLO: 95% of requests complete in < 200ms
```

### SLA (Service Level Agreement)
A contract with customers about SLOs. Violating an SLA has consequences (refunds, penalties).

### Error Budget
The amount of unreliability you're allowed before violating your SLO.

```
SLO: 99.9% availability
Error budget: 0.1% = 43.8 minutes/month

If you've used 30 minutes of downtime this month:
  Remaining error budget: 13.8 minutes
  
If you've used all 43.8 minutes:
  Error budget exhausted → freeze new deployments
  Focus on reliability until next month
```

**Why error budgets matter**: They create a shared language between dev and ops. "We have 10 minutes of error budget left this month" is more actionable than "we need to be more reliable."

---

## 4. Alerting Best Practices

### Alert on Symptoms, Not Causes

```
BAD: Alert when CPU > 90%
  (CPU might be high for legitimate reasons)

GOOD: Alert when error rate > 1%
  (Users are experiencing errors — that's what matters)
```

### The Four Golden Signals as Alerts

```yaml
# Prometheus alerting rules
- alert: HighErrorRate
  expr: rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m]) > 0.01
  for: 5m
  annotations:
    summary: "Error rate > 1% for 5 minutes"

- alert: HighLatency
  expr: histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m])) > 0.5
  for: 5m
  annotations:
    summary: "p99 latency > 500ms for 5 minutes"

- alert: LowCacheHitRate
  expr: cache_hits / (cache_hits + cache_misses) < 0.8
  for: 10m
  annotations:
    summary: "Cache hit rate below 80%"
```

### Alert Fatigue

Too many alerts → engineers ignore them → real problems missed.

**Rules for good alerts**:
1. Every alert must be actionable (someone must be able to do something)
2. Every alert must be urgent (if it can wait until morning, it's not an alert)
3. Alerts should be rare (if you get 100 alerts/day, they're not alerts)
4. Alerts should have runbooks (what to do when this fires)

---

## 5. Observability Stack

```
Services → OpenTelemetry SDK → Collector
                                    │
                    ┌───────────────┼───────────────┐
                    ▼               ▼               ▼
              Prometheus         Jaeger           Loki
              (metrics)         (traces)          (logs)
                    │               │               │
                    └───────────────┴───────────────┘
                                    │
                                Grafana
                            (unified dashboard)
```

**OpenTelemetry**: Vendor-neutral SDK for instrumenting your code. Generates metrics, logs, and traces in a standard format.

```python
from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

# Auto-instrument FastAPI (adds traces to all endpoints)
FastAPIInstrumentor.instrument_app(app)

# Manual span creation
tracer = trace.get_tracer(__name__)

def process_order(order_id: str):
    with tracer.start_as_current_span("process_order") as span:
        span.set_attribute("order.id", order_id)
        # ... process order
        span.set_attribute("order.status", "confirmed")
```

---

## References
- [Google SRE Book: Monitoring Distributed Systems](https://sre.google/sre-book/monitoring-distributed-systems/)
- [OpenTelemetry Documentation](https://opentelemetry.io/docs/)
- [Prometheus Documentation](https://prometheus.io/docs/)
- [Jaeger Documentation](https://www.jaegertracing.io/docs/)
