# Day 2: Exercises — Networking & Protocols

---

## Exercise 1: Basic Comprehension (15 minutes)

Answer these questions:

1. A user in Sydney opens your app. Your servers are in Virginia. What is the approximate round-trip latency? What can you do to reduce it?

2. You're building a multiplayer game. Should you use TCP or UDP for game state updates? Why? What about for the initial login?

3. A colleague says "we should use HTTP/1.1 because it's simpler." What are the performance implications of this choice at scale?

4. Your API returns user profile data that changes once per day. What `Cache-Control` header would you set? What about for a user's private messages?

5. What's the difference between a 401 and a 403 response? Give a real-world example of each.

---

## Exercise 2: Hands-On — Trace a Request (20 minutes)

### Option A: Run the code
```bash
cd code-examples/
python request_tracer.py https://httpbin.org/get
```

### Option B: Use browser DevTools
1. Open Chrome/Firefox DevTools (F12)
2. Go to the Network tab
3. Navigate to any website
4. Click on the first request
5. Find and record:
   - DNS lookup time
   - TCP connection time
   - TLS handshake time
   - Time to first byte (TTFB)
   - Total download time

Answer:
1. Which phase took the longest?
2. What HTTP version was used?
3. How many requests were made in total?
4. Which requests were served from cache?

---

## Exercise 3: Design Problem (25 minutes)

### Scenario: Global Chat Application

You're designing a chat application like WhatsApp:
- 500 million users worldwide
- Users expect messages to appear in under 100ms
- Users need to know when friends are online (presence)
- Messages must be delivered even if the recipient is offline

**Questions**:
1. Should you use HTTP or WebSockets for message delivery? Why?
2. How would you handle presence (online/offline status)?
3. How would you reduce latency for users in different regions?
4. What happens when a user's connection drops? How do you handle message delivery?

Draw a simple architecture diagram showing:
- Client connections
- Server topology
- How messages flow from sender to recipient

---

## Exercise 4: Critical Thinking — Protocol Selection (20 minutes)

For each scenario below, choose the best protocol/approach and justify your choice:

| Scenario | Options | Your Choice | Why |
|----------|---------|-------------|-----|
| Live stock price updates | HTTP polling, WebSocket, SSE | ? | ? |
| File upload (1GB) | HTTP POST, WebSocket, UDP | ? | ? |
| DNS query | TCP, UDP | ? | ? |
| Video call | TCP, UDP, WebRTC | ? | ? |
| REST API for user profiles | HTTP/1.1, HTTP/2, gRPC | ? | ? |
| IoT sensor data (lossy network) | TCP, UDP, MQTT | ? | ? |

---

## Exercise 5: Challenge — CDN Strategy Design (30 minutes)

### Scenario: Video Streaming Platform

You're designing the CDN strategy for a Netflix-like platform:
- 200 million users globally
- Average video: 2GB
- Peak: 10 million concurrent streams
- Content library: 5,000 titles
- 20% of titles account for 80% of views (Pareto principle)

**Design the CDN strategy**:

1. **Cache placement**: Where do you put CDN edge nodes? (Think: where are your users?)

2. **Cache sizing**: You can't cache all 5,000 titles at every edge. What do you cache where?

3. **Cache invalidation**: A movie gets taken down due to licensing. How do you remove it from all CDN edges quickly?

4. **Origin protection**: If a CDN edge has a cache miss, it fetches from origin. How do you prevent the origin from being overwhelmed during a popular new release?

5. **Cost optimization**: CDN bandwidth is expensive. What strategies reduce cost while maintaining performance?

**Hint for Q4**: Look up "thundering herd problem" and "request coalescing."

---

## Hints

**Exercise 1, Q1**: Speed of light in fiber is ~200,000 km/s. Sydney to Virginia is ~16,000 km.

**Exercise 3**: Think about what happens when a user sends a message. Does the server need to push it to the recipient, or can the recipient poll?

**Exercise 4, Video call**: WebRTC is built on UDP. Why does that make sense for video calls?

**Exercise 5, Q4**: What if multiple CDN edge servers all get a cache miss at the same time for the same content?

---

## Self-Assessment Checklist

- [ ] I can trace a full HTTP request from browser to server
- [ ] I know when to use TCP vs. UDP
- [ ] I understand what a CDN does and why it reduces latency
- [ ] I can choose between HTTP polling, WebSockets, and SSE
- [ ] I understand TLS and why it adds latency
- [ ] I know the most important HTTP status codes
