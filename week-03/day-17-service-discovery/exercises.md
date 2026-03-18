# Day 17: Exercises — Service Discovery & Service Mesh

---

## Exercise 1: Basic Comprehension (15 minutes)

1. Why can't you hardcode IP addresses for service-to-service communication in a microservices architecture?

2. What's the difference between client-side and server-side service discovery? Give a real-world example of each.

3. Describe the three states of a circuit breaker. What triggers each transition?

4. What is the sidecar pattern? What are the benefits of running a proxy sidecar alongside every service?

5. Why do retries need "jitter"? What problem does jitter solve?

---

## Exercise 2: Circuit Breaker Design (25 minutes)

### Scenario

Your Order Service calls these downstream services:
- Payment Service (critical — order can't complete without it)
- Recommendation Service (non-critical — nice to have)
- Analytics Service (non-critical — background tracking)
- Inventory Service (critical — must reserve items)

**Design circuit breakers for each**:

| Service | Critical? | Circuit Breaker Config | Fallback Behavior |
|---------|-----------|----------------------|-------------------|
| Payment | Yes | ? | ? |
| Recommendation | No | ? | ? |
| Analytics | No | ? | ? |
| Inventory | Yes | ? | ? |

For each:
1. What failure threshold triggers the circuit to open?
2. What timeout before trying again (half-open)?
3. What's the fallback behavior when the circuit is open?

---

## Exercise 3: Service Mesh Design (25 minutes)

### Scenario

You have 8 microservices. You need to implement:
- mTLS between all services
- Distributed tracing
- Automatic retries for transient failures
- Circuit breaking
- Traffic splitting (for canary deployments)

**Without a service mesh**: Each team must implement all of this in their service.

**With a service mesh**: The mesh handles it transparently.

**Design the service mesh**:
1. Which service mesh would you choose? (Istio, Linkerd, Consul Connect)
2. How do you configure mTLS? (Certificate rotation, trust anchors)
3. How do you configure retries? (Which status codes? How many retries? Backoff?)
4. How do you do a canary deployment? (Route 5% of traffic to new version)
5. What's the performance overhead of the sidecar proxy?

---

## Exercise 4: Cascading Failure Analysis (20 minutes)

### Scenario

```
User Request → API Gateway → Order Service → Payment Service
                                           → Inventory Service
                                           → Notification Service
```

Payment Service starts returning 500 errors (database issue).

**Trace the cascading failure**:
1. What happens to Order Service when Payment Service fails?
2. What happens to API Gateway when Order Service is slow?
3. What happens to other users when the thread pool fills up?
4. How does a circuit breaker prevent this cascade?
5. What should Order Service return to users when Payment Service is down?

---

## Exercise 5: Challenge — Design Service Discovery for a Global System (35 minutes)

### Scenario

You have a microservices system deployed in 3 regions (US, EU, APAC). Each region has 50 services, each running 3-10 instances.

**Design the service discovery architecture**:

1. **Registry topology**: One global registry or one per region? What are the tradeoffs?

2. **Cross-region calls**: Service A in US needs to call Service B. Should it call the US instance or the nearest instance? How does it know?

3. **Registry failure**: The service registry goes down. What happens to service-to-service calls? How do you make the registry highly available?

4. **Health checks**: How do you detect that a service instance is unhealthy? What's the health check interval? What happens when an instance fails a health check?

5. **DNS vs. registry**: Kubernetes uses DNS for service discovery. What are the limitations of DNS-based discovery compared to a dedicated registry?

---

## Hints

**Exercise 2**: For non-critical services, the fallback can be "return empty/default data." For critical services, the fallback might be "return an error to the user."

**Exercise 4**: Thread pool exhaustion is the key mechanism. When Payment Service is slow, Order Service threads are blocked waiting. Eventually all threads are blocked and Order Service can't handle new requests.

**Exercise 5, Q3**: The registry itself needs to be highly available. Use a distributed consensus system (etcd, ZooKeeper) for the registry.

---

## Self-Assessment Checklist

- [ ] I can explain client-side vs. server-side service discovery
- [ ] I understand the three states of a circuit breaker
- [ ] I can design fallback behavior for circuit-broken services
- [ ] I understand what a service mesh provides
- [ ] I can explain the sidecar proxy pattern
- [ ] I understand how cascading failures occur and how to prevent them
