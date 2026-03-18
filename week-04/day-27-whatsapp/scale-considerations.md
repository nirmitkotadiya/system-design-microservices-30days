# WhatsApp: Scale Considerations

## The Numbers

WhatsApp is one of the most efficient large-scale systems ever built:

- 2+ billion users
- 100+ billion messages per day
- 2+ billion minutes of voice/video calls per day
- 700+ million photos shared per day
- Only ~50 engineers when acquired by Facebook for $19B (2014)
- Each server handles ~1 million connections

The last point is remarkable. WhatsApp achieved massive scale with a tiny team by making smart technology choices.

---

## The Core Scaling Challenge: Persistent Connections

Unlike HTTP (request-response), messaging requires persistent connections. The server needs to push messages to clients in real-time.

```
HTTP model (bad for messaging):
  Client → "Any new messages?" → Server → "No"
  Client → "Any new messages?" → Server → "No"
  Client → "Any new messages?" → Server → "Yes, here's 1 message"
  (polling wastes bandwidth and battery)

WebSocket model (good for messaging):
  Client ←→ Server (persistent connection)
  Server → "New message!" → Client (instant delivery)
```

### The C10M Problem

WhatsApp needed to handle millions of concurrent connections per server. This is the "C10M problem" (10 million concurrent connections).

**Why this is hard**:
- Traditional thread-per-connection model: 1M connections = 1M threads = ~1TB RAM just for thread stacks
- Linux default: 1MB stack per thread

**WhatsApp's solution: Erlang/XMPP**

Erlang was designed for telecom systems that need millions of concurrent lightweight processes:
- Erlang processes: ~300 bytes each (vs 1MB for OS threads)
- 1M Erlang processes = ~300MB RAM
- Built-in message passing, fault tolerance, hot code reloading

```
WhatsApp server stack:
  - Erlang/OTP for connection handling
  - XMPP protocol (extended for WhatsApp features)
  - FreeBSD OS (better network performance than Linux at the time)
  - Custom patches to handle millions of connections
```

---

## Message Delivery Architecture

### The Delivery Guarantee Problem

WhatsApp shows three states for every message:
- ✓ (one check): Message sent to server
- ✓✓ (two checks): Message delivered to recipient's device
- ✓✓ (blue checks): Message read by recipient

Implementing this reliably at 100B messages/day is non-trivial.

```
Message flow:
  Sender → Server → Recipient

  1. Sender sends message
  2. Server stores message (recipient offline? store until online)
  3. Server sends ACK to sender → ✓ (sent)
  4. Server delivers to recipient
  5. Recipient's device sends delivery receipt → ✓✓ (delivered)
  6. Recipient opens message → read receipt → ✓✓ blue (read)

If recipient is offline:
  - Server stores message
  - When recipient comes online, server delivers queued messages
  - Messages stored for 30 days, then deleted
```

### Message Storage: Ephemeral by Design

WhatsApp's original design: messages are NOT stored on servers long-term. Once delivered, they're deleted. This is both a privacy feature and a scaling decision.

```
Storage model:
  - Messages in transit: stored in server queue (temporary)
  - Delivered messages: deleted from server
  - Message history: stored on device only
  - Media: stored in separate media servers, URL sent in message

Contrast with iMessage/Telegram:
  - Store messages in cloud (sync across devices)
  - Requires much more storage
  - Privacy tradeoff
```

---

## End-to-End Encryption at Scale

WhatsApp uses the Signal Protocol for E2E encryption. Every message is encrypted on the sender's device and can only be decrypted by the recipient.

```
Key exchange (simplified):
  Alice and Bob each have:
    - Identity key pair (long-term)
    - Signed prekey pair (medium-term)
    - One-time prekeys (single use)

  When Alice wants to message Bob:
    1. Alice fetches Bob's public keys from WhatsApp server
    2. Alice computes shared secret using Diffie-Hellman
    3. Alice encrypts message with shared secret
    4. Server stores encrypted blob (can't read it)
    5. Bob decrypts with his private key

WhatsApp server never sees message content.
```

**Scale challenge**: Key distribution for 2B users. WhatsApp maintains a key server that stores public keys for all users. When you message someone new, you fetch their public key.

---

## Group Messaging at Scale

Group chats are significantly harder than 1:1 messaging.

```
Naive approach (fan-out on write):
  Group with 256 members
  Alice sends message
  → Server sends 255 copies (one to each member)
  
  At scale:
  1B group messages/day × 100 avg group size = 100B deliveries/day
  (10x amplification!)

WhatsApp's approach:
  - Server sends ONE message to the group
  - Each recipient's device fetches it
  - Sender's device encrypts for each recipient separately
    (E2E encryption requires this)
  
  For large groups (256 members):
  - Sender encrypts 256 times (once per recipient)
  - This is done on the sender's device
  - Server stores one copy per recipient
```

---

## Media Handling

Photos, videos, and documents are handled separately from text messages.

```
Media upload flow:
  1. Client compresses and encrypts media on device
  2. Client uploads to WhatsApp media servers (separate from message servers)
  3. Server returns URL + decryption key
  4. Client sends text message containing URL + key
  5. Recipient downloads media from URL, decrypts with key

Benefits:
  - Message servers stay fast (no large blobs)
  - Media can be CDN-cached
  - Media servers can scale independently
  - Server can't read media (E2E encrypted)

Media storage:
  - Stored for 30 days after last download
  - Then deleted (ephemeral design)
  - Users must save to device if they want to keep it
```

---

## Handling 100x Growth

### Phase 1: 0-100M users
- Single Erlang cluster
- Simple message queue
- Basic media storage

### Phase 2: 100M-1B users
- Multiple Erlang clusters (sharded by user)
- Distributed message queues
- CDN for media delivery
- Read replicas for user data

### Phase 3: 1B-2B users
- Multi-region deployment
- Custom XMPP extensions
- Business API (WhatsApp Business)
- Voice/video calling infrastructure
- Status feature (Stories)

---

## The Erlang Choice: Why It Matters

Most messaging apps use Node.js, Go, or Java. WhatsApp chose Erlang. Why?

```
Erlang advantages for messaging:
  1. Lightweight processes (millions per server)
  2. Built-in fault tolerance (supervisor trees)
  3. Hot code reloading (deploy without downtime)
  4. Message passing model (natural fit for messaging)
  5. Battle-tested in telecom (Ericsson, 1986)

The result:
  - WhatsApp: ~50 engineers, 2B users
  - Typical messaging app: 500+ engineers for same scale
  
"The right tool for the job" taken to an extreme.
```

---

## Key Lessons

1. **Technology choice matters enormously** — Erlang let WhatsApp do more with less
2. **Ephemeral by design** — not storing messages long-term simplifies everything
3. **Separate message metadata from content** — fast path for text, separate path for media
4. **E2E encryption is a feature, not a constraint** — it also reduces server storage requirements
5. **Persistent connections require different architecture** — WebSockets/XMPP, not HTTP polling
6. **Group messaging amplifies everything** — design for it from the start
