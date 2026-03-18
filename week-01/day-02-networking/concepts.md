# Day 2: Networking & Protocols — Concepts Deep Dive

## 1. The Full Request Journey

When you type `https://twitter.com` and press Enter, here's what happens:

```
1. DNS Resolution      → "What IP address is twitter.com?"
2. TCP Connection      → "Establish a reliable connection"
3. TLS Handshake       → "Verify identity and encrypt"
4. HTTP Request        → "GET /home HTTP/2"
5. Server Processing   → Business logic, DB queries
6. HTTP Response       → HTML, JSON, etc.
7. Connection Reuse    → Keep-alive for subsequent requests
```

Each step has latency. Understanding each step helps you optimize the right one.

---

## 2. The OSI Model (Simplified)

You don't need to memorize all 7 layers, but you need to understand the relevant ones:

```
Layer 7: Application  → HTTP, gRPC, WebSocket (what your app uses)
Layer 4: Transport    → TCP, UDP (reliability vs. speed)
Layer 3: Network      → IP (routing between machines)
Layer 2: Data Link    → Ethernet, WiFi (local network)
Layer 1: Physical     → Cables, radio waves
```

For system design, you mostly care about Layers 3, 4, and 7.

---

## 3. TCP vs. UDP

### TCP (Transmission Control Protocol)
**Guarantee**: Every packet arrives, in order, exactly once.

How it achieves this:
- **3-way handshake** before data transfer (SYN → SYN-ACK → ACK)
- **Acknowledgments** for every packet
- **Retransmission** of lost packets
- **Flow control** to prevent overwhelming the receiver

```
Client          Server
  │──── SYN ────▶│   "I want to connect"
  │◀─ SYN-ACK ──│   "OK, I'm ready"
  │──── ACK ────▶│   "Great, let's go"
  │              │
  │── Data ─────▶│
  │◀─── ACK ────│   "Got it"
```

**Cost**: ~1.5 round trips before data flows. Adds latency.

**Use TCP when**: Data integrity matters (HTTP, databases, file transfer, email)

### UDP (User Datagram Protocol)
**Guarantee**: None. Packets may be lost, duplicated, or arrive out of order.

**Benefit**: No handshake, no acknowledgments, no retransmission. Just send.

**Use UDP when**: Speed matters more than reliability:
- Video streaming (a dropped frame is better than a frozen video)
- Online gaming (old position data is useless anyway)
- DNS lookups (small, fast, can retry if lost)
- VoIP (slight audio glitch beats 2-second delay)

### The Tradeoff Table

| Feature | TCP | UDP |
|---------|-----|-----|
| Reliability | Guaranteed | Best-effort |
| Ordering | In-order | No guarantee |
| Speed | Slower (overhead) | Faster |
| Connection | Connection-oriented | Connectionless |
| Use case | HTTP, DB, email | Video, gaming, DNS |

---

## 4. DNS — The Internet's Phone Book

DNS (Domain Name System) translates human-readable names to IP addresses.

### The DNS Resolution Chain

```
Browser asks: "What's the IP for api.twitter.com?"

1. Check local cache → Not found
2. Ask OS resolver → Not found
3. Ask Recursive Resolver (your ISP or 8.8.8.8)
   a. Ask Root Nameserver → "Try .com nameservers"
   b. Ask .com Nameserver → "Try twitter.com nameservers"
   c. Ask twitter.com Nameserver → "api.twitter.com = 104.244.42.1"
4. Cache the result (TTL: 300 seconds)
5. Return IP to browser
```

### Why DNS Matters for System Design

**TTL (Time To Live)**: How long DNS records are cached.
- Low TTL (60s): Changes propagate fast, but more DNS queries
- High TTL (86400s): Fewer queries, but changes take a day to propagate

**DNS-based Load Balancing**: Return multiple IPs for the same domain. Clients pick one.

**DNS Failover**: Change the IP when a server goes down. But TTL means it takes time.

**GeoDNS**: Return different IPs based on where the client is. Used by CDNs.

---

## 5. HTTP — The Language of the Web

### HTTP/1.1 (1997)
- One request per TCP connection (or pipelining, which is buggy)
- **Head-of-line blocking**: Request 2 waits for Request 1 to complete
- Text-based headers (verbose, uncompressed)

```
GET /api/users HTTP/1.1
Host: api.example.com
Accept: application/json
Authorization: Bearer eyJhbGc...
```

### HTTP/2 (2015)
Key improvements:
- **Multiplexing**: Multiple requests over one TCP connection simultaneously
- **Header compression** (HPACK): Reduces overhead
- **Server push**: Server can send resources before client asks
- **Binary protocol**: More efficient than text

```
HTTP/1.1: Request 1 → Response 1 → Request 2 → Response 2
HTTP/2:   Request 1 ─────────────────────────▶ Response 1
          Request 2 ─────────────────────────▶ Response 2
          (Both in flight simultaneously)
```

### HTTP/3 (2022)
Built on QUIC (UDP-based) instead of TCP:
- Eliminates TCP head-of-line blocking
- Faster connection establishment (0-RTT in some cases)
- Better performance on lossy networks (mobile)

### HTTP Status Codes You Must Know

| Code | Meaning | When to Use |
|------|---------|-------------|
| 200 | OK | Successful GET/PUT |
| 201 | Created | Successful POST |
| 204 | No Content | Successful DELETE |
| 301 | Moved Permanently | Permanent redirect |
| 302 | Found | Temporary redirect |
| 400 | Bad Request | Client sent invalid data |
| 401 | Unauthorized | Not authenticated |
| 403 | Forbidden | Authenticated but not authorized |
| 404 | Not Found | Resource doesn't exist |
| 429 | Too Many Requests | Rate limited |
| 500 | Internal Server Error | Server bug |
| 503 | Service Unavailable | Server overloaded/down |

---

## 6. TLS/HTTPS — Encryption in Transit

TLS (Transport Layer Security) provides:
1. **Encryption**: Data is unreadable to eavesdroppers
2. **Authentication**: You're talking to the real server (via certificates)
3. **Integrity**: Data wasn't tampered with in transit

### The TLS Handshake (simplified)

```
Client                          Server
  │──── ClientHello ───────────▶│  "I support TLS 1.3, here are my cipher suites"
  │◀─── ServerHello ────────────│  "Let's use AES-256-GCM, here's my certificate"
  │──── Verify cert ────────────│  (Client verifies cert against CA)
  │──── Key Exchange ───────────▶│  "Here's my public key"
  │◀─── Finished ───────────────│  "Encrypted channel established"
  │══════ Encrypted Data ════════│
```

**Cost**: TLS adds ~1 round trip. TLS 1.3 reduced this from 2 round trips to 1.

**For system design**: Always use TLS for external traffic. For internal service-to-service traffic, mTLS (mutual TLS) is best practice.

---

## 7. WebSockets — Persistent Bidirectional Communication

HTTP is request-response: client asks, server answers. But what if the server needs to push data to the client without being asked?

**Use cases**: Chat apps, live notifications, real-time dashboards, multiplayer games

### How WebSockets Work

```
1. Client sends HTTP Upgrade request:
   GET /chat HTTP/1.1
   Upgrade: websocket
   Connection: Upgrade

2. Server responds:
   HTTP/1.1 101 Switching Protocols
   Upgrade: websocket

3. Now both sides can send messages at any time:
   Client → Server: {"type": "message", "text": "Hello"}
   Server → Client: {"type": "message", "text": "Hi back!"}
   Server → Client: {"type": "notification", "text": "New follower!"}
```

### WebSockets vs. Alternatives

| Approach | How It Works | Latency | Server Load | Use Case |
|----------|-------------|---------|-------------|----------|
| Short polling | Client asks every N seconds | High | High | Simple notifications |
| Long polling | Client asks, server holds until data | Medium | Medium | Chat (legacy) |
| WebSockets | Persistent bidirectional connection | Low | Low | Real-time apps |
| Server-Sent Events | Server pushes, client reads | Low | Low | One-way updates |

---

## 8. CDN — Content Delivery Networks

A CDN is a geographically distributed network of servers that caches content close to users.

```
Without CDN:
User in Tokyo → Server in Virginia (150ms latency)

With CDN:
User in Tokyo → CDN Edge in Tokyo (5ms latency)
                CDN Edge → Origin in Virginia (only for cache misses)
```

### What CDNs Cache
- Static assets: images, CSS, JavaScript, fonts
- API responses (with proper cache headers)
- Video content (Netflix uses CDNs heavily)

### CDN Cache Headers
```http
Cache-Control: public, max-age=86400    # Cache for 24 hours
Cache-Control: private, no-cache        # Don't cache (user-specific)
ETag: "abc123"                          # Version identifier for cache validation
```

### CDN Architecture

```
                    ┌─────────────────┐
                    │  Origin Server  │
                    │  (Virginia)     │
                    └────────┬────────┘
                             │
          ┌──────────────────┼──────────────────┐
          │                  │                  │
   ┌──────▼──────┐   ┌───────▼──────┐   ┌──────▼──────┐
   │ CDN Edge    │   │  CDN Edge    │   │  CDN Edge   │
   │ (Tokyo)     │   │  (London)    │   │  (São Paulo)│
   └──────┬──────┘   └───────┬──────┘   └──────┬──────┘
          │                  │                  │
   Tokyo Users        London Users       Brazil Users
```

---

## 9. Common Networking Pitfalls in System Design

### Chatty Microservices
Making too many small network calls instead of batching:
```
BAD:  100 services × 1 DB call each = 100 network round trips
GOOD: 1 service × 1 batched DB call = 1 network round trip
```

### Ignoring Network Partitions
Networks fail. Design for it. Use timeouts, retries with backoff, and circuit breakers.

### Not Using Connection Pooling
Opening a new TCP connection for every request is expensive. Use connection pools.

### Forgetting About DNS TTL
When you change a server's IP, DNS changes don't propagate instantly. Plan for this.

---

## References
- DDIA Chapter 8: The Trouble with Distributed Systems (network failures)
- [HTTP/2 Explained](https://http2-explained.haxx.se/)
- [How DNS Works](https://howdns.works/)
- [WebSocket RFC 6455](https://tools.ietf.org/html/rfc6455)
