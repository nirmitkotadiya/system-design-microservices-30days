# Day 3: Load Balancing — Concepts Deep Dive

## 1. What Is a Load Balancer?

A load balancer is a component that distributes incoming network traffic across multiple backend servers. It sits between clients and servers, acting as a reverse proxy.

```
                    ┌─────────────────┐
Clients ──────────▶ │  Load Balancer  │ ──────────▶ Server 1
                    │                 │ ──────────▶ Server 2
                    └─────────────────┘ ──────────▶ Server 3
```

### Why You Need One
- **Availability**: If one server dies, traffic routes to healthy servers
- **Scalability**: Add servers without changing client configuration
- **Performance**: Distribute load to prevent any single server from being overwhelmed
- **Maintenance**: Take servers offline for updates without downtime

---

## 2. Load Balancing Algorithms

### Algorithm 1: Round Robin
**How it works**: Requests go to servers in rotation: 1, 2, 3, 1, 2, 3...

```
Request 1 → Server 1
Request 2 → Server 2
Request 3 → Server 3
Request 4 → Server 1  (back to start)
```

**Pros**: Simple, even distribution of request count  
**Cons**: Doesn't account for request weight (a 10ms request and a 10s request count the same)  
**Best for**: Stateless services with similar request complexity

### Algorithm 2: Weighted Round Robin
**How it works**: Servers get requests proportional to their weight.

```
Server 1: weight=3 (powerful)
Server 2: weight=1 (less powerful)

Sequence: 1, 1, 1, 2, 1, 1, 1, 2...
```

**Best for**: Heterogeneous server pools (different hardware specs)

### Algorithm 3: Least Connections
**How it works**: New request goes to the server with the fewest active connections.

```
Server 1: 10 active connections
Server 2: 3 active connections  ← Next request goes here
Server 3: 7 active connections
```

**Pros**: Better for variable-length requests  
**Cons**: Requires tracking connection counts (more state)  
**Best for**: Long-lived connections (WebSockets, database connections)

### Algorithm 4: IP Hash (Sticky by IP)
**How it works**: Hash the client's IP address to determine which server handles it. Same IP always goes to same server.

```
hash("192.168.1.1") % 3 = 0 → Server 1 (always)
hash("10.0.0.5") % 3 = 2 → Server 3 (always)
```

**Pros**: Client always hits the same server (useful for stateful apps)  
**Cons**: Uneven distribution if some IPs generate more traffic; fails if server goes down  
**Best for**: Legacy stateful applications that can't be made stateless

### Algorithm 5: Random
**How it works**: Pick a random server.

**Pros**: Simple, no state required  
**Cons**: Can be uneven in the short term  
**Best for**: Large server pools where statistical distribution is sufficient

### Algorithm 6: Least Response Time
**How it works**: Route to the server with the lowest average response time AND fewest connections.

**Pros**: Best for performance-sensitive applications  
**Cons**: Requires measuring response times (overhead)  
**Best for**: Heterogeneous workloads where server performance varies

### Comparison Table

| Algorithm | State Required | Best For | Weakness |
|-----------|---------------|----------|----------|
| Round Robin | None | Uniform requests | Ignores request weight |
| Weighted RR | Weights | Mixed hardware | Static weights |
| Least Connections | Connection counts | Long requests | Overhead |
| IP Hash | Hash table | Stateful apps | Uneven distribution |
| Least Response Time | Response times | Performance-critical | Measurement overhead |

---

## 3. Layer 4 vs. Layer 7 Load Balancing

### Layer 4 (Transport Layer)
Operates at the TCP/UDP level. Doesn't look at the content of packets.

```
Client → LB → Server
         ↑
    Only sees: source IP, dest IP, port
    Doesn't see: HTTP headers, URL, cookies
```

**Pros**: Very fast (no packet inspection), works for any TCP/UDP protocol  
**Cons**: Can't make routing decisions based on content  
**Examples**: AWS NLB, HAProxy (TCP mode)

### Layer 7 (Application Layer)
Operates at the HTTP level. Can inspect request content.

```
Client → LB → Server
         ↑
    Can see: HTTP method, URL, headers, cookies, body
    Can route: /api/* → API servers, /static/* → CDN
```

**Pros**: Content-based routing, SSL termination, request modification  
**Cons**: Slower (must parse HTTP), more complex  
**Examples**: AWS ALB, Nginx, HAProxy (HTTP mode)

### When to Use Each

| Use Case | L4 | L7 |
|----------|----|----|
| Simple TCP load balancing | ✓ | |
| Route /api to API servers | | ✓ |
| Route /admin to admin servers | | ✓ |
| SSL termination | | ✓ |
| WebSocket support | ✓ | ✓ |
| Maximum throughput | ✓ | |
| A/B testing | | ✓ |

---

## 4. Health Checks

A load balancer must know which servers are healthy. It does this via health checks.

### Active Health Checks
The LB periodically sends a request to each server:

```
Every 10 seconds:
LB → Server 1: GET /health → 200 OK ✓ (healthy)
LB → Server 2: GET /health → 200 OK ✓ (healthy)
LB → Server 3: GET /health → timeout ✗ (unhealthy)

Result: Remove Server 3 from rotation
```

### Passive Health Checks
The LB monitors real traffic for failures:

```
Request → Server 3 → Connection refused
LB marks Server 3 as unhealthy after N failures
```

### What a Good Health Check Endpoint Does
```python
@app.get("/health")
def health_check():
    # Check database connectivity
    db.execute("SELECT 1")
    # Check cache connectivity
    cache.ping()
    # Check disk space
    assert disk_free() > 1_000_000_000  # 1GB free
    return {"status": "healthy"}
```

A health check should verify that the server can actually serve traffic, not just that it's running.

---

## 5. Sticky Sessions (Session Affinity)

**Problem**: If a user's session is stored on Server 1, and the next request goes to Server 2, the user appears logged out.

**Solution**: Sticky sessions — route the same user to the same server.

### Cookie-Based Stickiness
```
First request:
Client → LB → Server 1
LB sets cookie: SERVERID=server1

Subsequent requests:
Client sends cookie: SERVERID=server1
LB routes to Server 1
```

### IP-Based Stickiness
Use IP hash algorithm (see above).

### The Problem with Sticky Sessions
```
Server 1: 1000 sticky users (heavy load)
Server 2: 100 sticky users (light load)
Server 3: 50 sticky users (very light load)
```

Sticky sessions break even load distribution. The right solution is to make your application stateless and store sessions in a shared cache (Redis).

---

## 6. Global Load Balancing

For global applications, you need load balancing at the DNS level:

```
User in Tokyo → DNS → Tokyo servers
User in London → DNS → London servers
User in New York → DNS → Virginia servers
```

This is called **GeoDNS** or **Global Server Load Balancing (GSLB)**.

### How It Works
1. DNS server detects client's geographic location (via IP)
2. Returns the IP of the nearest server cluster
3. Client connects to that cluster

**Providers**: AWS Route 53 (latency-based routing), Cloudflare, Akamai

---

## 7. Real-World Load Balancer Configurations

### Nginx Round Robin
```nginx
upstream backend {
    server server1.example.com;
    server server2.example.com;
    server server3.example.com;
}

server {
    listen 80;
    location / {
        proxy_pass http://backend;
    }
}
```

### Nginx Least Connections
```nginx
upstream backend {
    least_conn;
    server server1.example.com;
    server server2.example.com;
}
```

### Nginx Weighted
```nginx
upstream backend {
    server server1.example.com weight=3;
    server server2.example.com weight=1;
}
```

---

## 8. Common Pitfalls

### The Thundering Herd
When a server comes back online after being down, the LB sends it a flood of requests. The server may crash again immediately.

**Solution**: Slow start — gradually increase traffic to a recovering server.

### Ignoring Connection Draining
When removing a server from rotation, existing connections should be allowed to complete.

**Solution**: Connection draining — stop sending new requests but let existing ones finish.

### Not Monitoring the Load Balancer Itself
The LB is a single point of failure. Use active-passive or active-active LB pairs.

---

## References
- [Nginx Load Balancing Documentation](https://docs.nginx.com/nginx/admin-guide/load-balancer/http-load-balancer/)
- [AWS Elastic Load Balancing](https://aws.amazon.com/elasticloadbalancing/)
- DDIA Chapter 1: Scalability section
