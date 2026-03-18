# My WhatsApp Design — Learner Template

Practice designing a messaging system like WhatsApp. The key challenges are persistent connections at scale, message delivery guarantees, and end-to-end encryption.

---

## Step 1: Clarify Requirements (5 minutes)

**Functional Requirements**:
- [ ] 1:1 messaging
- [ ] Group messaging (max ___ members)
- [ ] Message delivery receipts (sent/delivered/read)
- [ ] Media sharing (photos, videos, documents)
- [ ] Voice/video calls
- [ ] Other: _______________

**Non-Functional Requirements**:
- Daily active users: _______________
- Messages per day: _______________
- Message delivery latency: < ___ ms
- Availability: _______________
- End-to-end encryption: yes/no

**Out of Scope**:
- _______________

---

## Step 2: Capacity Estimation

```
Daily active users: ___
Messages per user per day: ___
Total messages per day: ___
Messages per second (peak): ___

Average message size: ___ bytes
Storage per day (messages): ___

Media messages: ___% of total
Average media size: ___ MB
Media storage per day: ___
```

---

## Step 3: High-Level Design

```
[Draw your architecture here]

Key components:
- Client apps (iOS, Android, Web)
- Connection servers (WebSocket/XMPP)
- Message routing service
- Message queue/storage
- Media servers
- User/contact service
- Notification service (push for offline users)
```

---

## Step 4: Deep Dive — Connection Management

How do you maintain persistent connections for 2B users?

**Protocol choice**:
- WebSockets?
- XMPP?
- Custom protocol?

**Why**: _______________

**How many connections per server?**
- With threads: ___ connections/server
- With async I/O: ___ connections/server

**How do you route a message to the right connection server?**
(User A is connected to Server 3, User B is connected to Server 7)
_______________

---

## Step 5: Deep Dive — Message Delivery

Design the message delivery flow with delivery receipts:

```
Sender sends message:
1. _______________
2. _______________
3. _______________

Recipient receives message:
1. _______________
2. _______________
3. _______________

Recipient is offline:
1. _______________
2. _______________
```

**How long do you store undelivered messages?**
_______________

**What happens if the server crashes before delivering?**
_______________

---

## Step 6: Deep Dive — Group Messaging

A group has 256 members. Alice sends a message.

**Your approach**:
- Fan-out on write (server sends 255 copies)?
- Fan-out on read (recipients fetch)?
- Hybrid?

**Tradeoffs**:
| Approach | Write cost | Read cost | Storage |
|----------|-----------|-----------|---------|
| Fan-out on write | | | |
| Fan-out on read | | | |

**Your choice and why**: _______________

---

## Step 7: Deep Dive — Media Handling

How do you handle photo/video sharing?

**Upload flow**:
```
1. _______________
2. _______________
3. _______________
```

**Storage strategy**:
- Where do you store media?
- How long do you keep it?
- How do you handle deduplication (same photo sent to multiple people)?

---

## Step 8: Deep Dive — End-to-End Encryption

How does E2E encryption work in your design?

**Key concepts**:
- Where are keys generated?
- Where are keys stored?
- What does the server see?
- How does key exchange work for new conversations?

**Impact on your architecture**:
- Can you store messages on the server?
- Can you search message content?
- What happens when a user gets a new phone?

---

## Step 9: Bottlenecks and Solutions

| Bottleneck | Solution |
|------------|----------|
| Millions of concurrent connections | |
| Message fan-out for large groups | |
| Offline message storage | |
| Media storage costs | |

---

## Self-Assessment

Compare to `../architecture-diagram.md` and `../scale-considerations.md`.

- [ ] Did I handle persistent connections at scale?
- [ ] Did I implement delivery receipts?
- [ ] Did I design group messaging?
- [ ] Did I handle offline users?
- [ ] Did I address media handling separately?
- [ ] Did I consider E2E encryption implications?

**What I got right**: _______________
**What I missed**: _______________
**What I'd do differently**: _______________
