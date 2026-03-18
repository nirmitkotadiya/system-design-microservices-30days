# WhatsApp Architecture Diagram

## Message Flow

```
Sender (Alice) → Chat Server → Recipient (Bob)

If Bob is online:
  Alice → Chat Server → Bob (direct delivery)
  Bob sends delivery receipt → Chat Server → Alice (✓✓)
  Bob reads message → Chat Server → Alice (✓✓ blue)

If Bob is offline:
  Alice → Chat Server → Message stored in offline queue
  Bob comes online → Chat Server delivers queued messages
  Bob sends delivery receipt → Chat Server → Alice
```

## Architecture

```
Alice's Phone                              Bob's Phone
     │                                          │
     │ WebSocket                                │ WebSocket
     │                                          │
┌────▼────────────────────────────────────────▼────┐
│                  Chat Server Cluster              │
│                                                   │
│  ┌──────────────┐    ┌──────────────────────┐    │
│  │ Connection   │    │   Message Router     │    │
│  │ Manager      │    │   (finds Bob's server)│    │
│  └──────────────┘    └──────────────────────┘    │
└───────────────────────────────────────────────────┘
         │                        │
    ┌────▼────┐              ┌────▼────────────────┐
    │ Message │              │  Offline Queue      │
    │  Store  │              │  (if Bob offline)   │
    │(Cassandra)             │  (Cassandra)        │
    └─────────┘              └─────────────────────┘
         │
    ┌────▼────────────────────────────────────────┐
    │              Kafka                           │
    │  (Message events for analytics, backup)      │
    └─────────────────────────────────────────────┘
```

## End-to-End Encryption (Signal Protocol)

```
Key Exchange (one-time, when Alice first messages Bob):
  1. Alice generates key pair (public/private)
  2. Bob generates key pair (public/private)
  3. Alice fetches Bob's public key from key server
  4. Both compute shared secret using Diffie-Hellman
  5. Shared secret used to encrypt messages

Message Encryption:
  Alice → Encrypt with Bob's public key → Ciphertext → Server → Bob
  Server NEVER sees plaintext
  Only Bob can decrypt (has private key)

WhatsApp server stores:
  - Encrypted messages (can't read them)
  - Public keys (for key exchange)
  - Message metadata (who sent to whom, when)
```

## Presence System

```
User comes online:
  1. Connect to chat server via WebSocket
  2. Chat server updates presence store: user_id → {online: true, last_seen: now}
  3. Notify contacts who are online

User goes offline:
  1. WebSocket disconnects
  2. Chat server updates: user_id → {online: false, last_seen: now}
  3. Notify contacts

Presence store: Redis
  Key: presence:{user_id}
  Value: {online: bool, last_seen: timestamp, server_id: string}
  TTL: 30 seconds (heartbeat required to stay "online")
```

## Group Message Fan-out

```
Alice sends message to group (1,024 members):

Option A: Server fan-out
  Server sends message to each of 1,024 members
  1,024 × message_size = large bandwidth

Option B: Client fan-out (WhatsApp's approach for small groups)
  Alice's phone sends to each member directly
  Encrypted separately for each recipient (E2E encryption)

Option C: Hybrid
  Small groups (< 100): client fan-out
  Large groups (> 100): server fan-out with group key
```
