# Day 17: Service Discovery & Service Mesh — Concepts Deep Dive

## 1. The Service Discovery Problem

In a monolith, calling another module is a function call. In microservices, it's a network call — and you need to know the IP and port.

```
Problem:
  Order Service needs to call Payment Service
  Payment Service runs on 10 instances
  Instances are added/removed dynamically (auto-scaling)
  IPs change when instances restart

Naive solution: Hardcode IPs
  payment_service_url = "http://10.0.1.5:8080"
  
  Problem: What when that instance is replaced?
           What about the other 9 instances?
```

---

## 2. Service Registry

A service registry is a database of service instances and their locations.

```
Service Registry (e.g., Consul, etcd, Eureka):

Service Name    | Instances
----------------|------------------------------------------
payment-service | 10.0.1.5:8080, 10.0.1.6:8080, 10.0.1.7:8080
order-service   | 10.0.2.1:8080, 10.0.2.2:8080
user-service    | 10.0.3.1:8080
```

Services register themselves on startup and deregister on shutdown. Health checks remove unhealthy instances.

---

## 3. Client-Side Discovery

The client queries the service registry and chooses an instance.

```
Order Service:
1. Query registry: "Where is payment-service?"
2. Registry returns: [10.0.1.5:8080, 10.0.1.6:8080, 10.0.1.7:8080]
3. Client picks one (round-robin, random, etc.)
4. Client calls: http://10.0.1.5:8080/payments
```

**Pros**: Client has full control over load balancing  
**Cons**: Client must implement discovery logic; each language needs its own library

**Examples**: Netflix Eureka + Ribbon

---

## 4. Server-Side Discovery

A load balancer queries the registry and routes requests.

```
Order Service:
1. Call: http://payment-service/payments
2. Load balancer intercepts
3. Load balancer queries registry
4. Load balancer routes to 10.0.1.5:8080
```

**Pros**: Client is simple (just calls a hostname)  
**Cons**: Load balancer is a single point of failure; extra network hop

**Examples**: AWS ALB + ECS, Kubernetes Services

---

## 5. DNS-Based Discovery

Use DNS to resolve service names to IPs.

```
payment-service.internal → [10.0.1.5, 10.0.1.6, 10.0.1.7]
```

Kubernetes uses this by default. Each service gets a DNS name.

**Pros**: Simple, works with any language  
**Cons**: DNS caching can cause stale entries; no health checking built in

---

## 6. Service Mesh

A service mesh is an infrastructure layer that handles service-to-service communication.

```
Without service mesh:
  Each service implements: retry logic, circuit breaking, mTLS, tracing, metrics
  
With service mesh:
  Sidecar proxy handles all of this transparently
  Services just make HTTP calls
```

### The Sidecar Pattern

```
┌─────────────────────────────────────────┐
│              Pod / Container            │
│                                         │
│  ┌──────────────┐   ┌────────────────┐  │
│  │   Service    │◄──│ Sidecar Proxy  │  │
│  │  (your code) │   │   (Envoy)      │  │
│  └──────────────┘   └────────┬───────┘  │
│                               │          │
└───────────────────────────────┼──────────┘
                                │ All traffic goes through sidecar
                                ▼
                    ┌─────────────────────┐
                    │   Control Plane     │
                    │   (Istio, Linkerd)  │
                    └─────────────────────┘
```

Every service gets a sidecar proxy (usually Envoy). All traffic goes through the sidecar. The control plane configures all sidecars.

### What a Service Mesh Provides

| Feature | Without Mesh | With Mesh |
|---------|-------------|-----------|
| mTLS | Manual per service | Automatic |
| Retries | Manual per service | Configured centrally |
| Circuit breaking | Manual per service | Configured centrally |
| Distributed tracing | Manual per service | Automatic |
| Metrics | Manual per service | Automatic |
| Traffic splitting | Manual | Configured centrally |
| Load balancing | Manual | Automatic |

---

## 7. Circuit Breakers

A circuit breaker prevents cascading failures by stopping calls to a failing service.

### The Three States

```
CLOSED (normal operation):
  Requests flow through
  Track failure rate
  If failure rate > threshold → OPEN

OPEN (service is failing):
  All requests fail immediately (no network call)
  After timeout → HALF-OPEN

HALF-OPEN (testing recovery):
  Allow a few requests through
  If they succeed → CLOSED
  If they fail → OPEN
```

### Why Circuit Breakers Matter

```
Without circuit breaker:
  Payment Service is slow (5s timeout)
  Order Service calls Payment Service
  Order Service waits 5 seconds per request
  Order Service's thread pool fills up
  Order Service becomes slow
  API Gateway calls Order Service
  API Gateway becomes slow
  Everything is slow → cascading failure

With circuit breaker:
  Payment Service is slow
  Circuit breaker opens after 5 failures
  Order Service fails fast (< 1ms)
  Order Service returns degraded response
  System remains responsive
```

### Implementation

```python
class CircuitBreaker:
    def __init__(self, failure_threshold=5, timeout=60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"

    def call(self, func, *args, **kwargs):
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.timeout:
                self.state = "HALF-OPEN"
            else:
                raise CircuitOpenError("Circuit is open")

        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise

    def _on_success(self):
        self.failure_count = 0
        self.state = "CLOSED"

    def _on_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
```

---

## 8. Retry Strategies

When a service call fails, should you retry?

### Exponential Backoff with Jitter

```python
def retry_with_backoff(func, max_retries=3, base_delay=1.0):
    for attempt in range(max_retries):
        try:
            return func()
        except TransientError as e:
            if attempt == max_retries - 1:
                raise
            # Exponential backoff with jitter
            delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
            time.sleep(delay)
```

**Why jitter?** Without jitter, all retrying clients retry at the same time, creating a thundering herd.

### What to Retry

- **Retry**: Network timeouts, 503 Service Unavailable, 429 Too Many Requests
- **Don't retry**: 400 Bad Request, 401 Unauthorized, 404 Not Found, 500 Internal Server Error (might be idempotency issue)

---

## References
- [Consul Documentation](https://www.consul.io/docs)
- [Istio Documentation](https://istio.io/latest/docs/)
- [Netflix Hystrix (Circuit Breaker)](https://github.com/Netflix/Hystrix/wiki)
- [Martin Fowler on Circuit Breakers](https://martinfowler.com/bliki/CircuitBreaker.html)
