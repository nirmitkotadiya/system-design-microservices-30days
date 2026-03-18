# Day 2: Networking & Protocols

## "How Does a Request Actually Get From Your Browser to a Database?"

**Estimated Time**: 90 minutes  
**Difficulty**: Beginner-Intermediate  
**Prerequisites**: Day 1 complete

---

## Learning Objectives
- Trace a full HTTP request from browser to database and back
- Explain TCP vs. UDP and when each is appropriate
- Describe what DNS does and why it matters for system design
- Explain HTTP/1.1 vs. HTTP/2 vs. HTTP/3 differences
- Understand what a CDN is and how it reduces latency
- Explain WebSockets and when to use them vs. HTTP

---

## Quick Summary

Every system design decision is ultimately about moving data between machines. Understanding how that data moves — the protocols, the latency, the failure modes — is foundational. Today you'll trace a request from a user's browser all the way to a database and back, understanding every hop along the way.

The core insight: **network calls are expensive**. Every protocol layer adds overhead. Every hop adds latency. Good system design minimizes unnecessary network calls.

---

## Files in This Folder

| File | Description |
|------|-------------|
| `concepts.md` | TCP/IP, HTTP, DNS, CDN, WebSockets deep dive |
| `exercises.md` | 5 exercises from request tracing to protocol selection |
| `code-examples/` | HTTP server, WebSocket demo, DNS lookup tool |
| `diagrams/` | Request flow diagrams |

---

## Success Criteria

You've mastered Day 2 when you can:
- [ ] Trace a full HTTP request through DNS, TCP, HTTP layers
- [ ] Explain the difference between TCP and UDP with examples
- [ ] Describe what happens during a TLS handshake
- [ ] Explain why HTTP/2 is faster than HTTP/1.1
- [ ] Describe when to use WebSockets vs. HTTP polling
- [ ] Explain how a CDN reduces latency

---

## Interview Questions for This Day
- "What happens when you type google.com into a browser?"
- "When would you use UDP instead of TCP?"
- "How does a CDN work?"
- "What's the difference between HTTP/1.1 and HTTP/2?"
