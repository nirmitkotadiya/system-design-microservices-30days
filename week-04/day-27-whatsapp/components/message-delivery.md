# WhatsApp Component: Message Delivery Service

## Overview

The message delivery service ensures every message is delivered exactly once, with accurate delivery receipts, even when recipients are offline.

## Message Flow

```
1. Alice sends "Hello Bob" from her phone
2. Alice's app encrypts the message with Bob's public key
3. Encrypted message sent to WhatsApp server over WebSocket
4. Server stores message in Bob's queue
5. Server sends ACK to Alice → ✓ (one check: sent to server)
6. If Bob is online: server delivers immediately
   If Bob is offline: message waits in queue (up to 30 days)
7. Bob's device receives message, sends delivery receipt
8. Server forwards receipt to Alice → ✓✓ (two checks: delivered)
9. Bob opens the message, app sends read receipt
10. Server forwards read receipt to Alice → ✓✓ blue (read)
```

## Message Queue Design

```python
# Message stored in server queue
{
    "message_id": "msg_abc123",
    "from_user": "alice_id",
    "to_user": "bob_id",
    "encrypted_content": "base64_encrypted_blob",
    "timestamp": 1704067200,
    "type": "text",  # text | image | video | audio | document
    "status": "pending",  # pending | delivered | read
    "expires_at": 1706659200  # 30 days from now
}

# Storage: one queue per user
# Key: "queue:{user_id}"
# Type: Redis List (LPUSH to add, RPOP to consume)
# Persistence: also written to database for durability
```

## Connection Routing

With millions of connection servers, how does the server know which server Bob is connected to?

```
Connection registry (Redis):
  Key: "connection:{user_id}"
  Value: "server_id:connection_id"
  TTL: 60 seconds (refreshed by heartbeat)

Message routing:
  1. Server receives message for Bob
  2. Look up: GET connection:bob_id → "server_7:conn_456"
  3. Forward message to server_7 via internal message bus
  4. Server_7 delivers to Bob's WebSocket connection

If Bob is offline:
  1. GET connection:bob_id → nil (not connected)
  2. Store in Bob's message queue
  3. Send push notification (APNs/FCM) to wake Bob's app
  4. When Bob reconnects, drain his queue
```

## Delivery Guarantees

WhatsApp uses at-least-once delivery with deduplication:

```python
def deliver_message(message_id, to_user):
    # Check if already delivered (idempotency)
    if redis.get(f"delivered:{message_id}"):
        return  # Already delivered, skip
    
    # Deliver to user
    connection = get_user_connection(to_user)
    if connection:
        connection.send(message)
        # Mark as delivered (with TTL to avoid infinite storage)
        redis.setex(f"delivered:{message_id}", 86400, "1")
        # Send delivery receipt back to sender
        send_receipt(message_id, "delivered")
    else:
        # Queue for later delivery
        queue_message(to_user, message_id)
```

## Handling Network Failures

```
Scenario: Server sends message to Bob, but Bob's connection drops
before he sends the delivery receipt.

Without idempotency:
  Server retries → Bob receives duplicate message

With idempotency:
  Each message has unique ID
  Bob's app checks: "Have I seen message_id=abc123?"
  If yes: send receipt but don't show duplicate
  If no: show message, send receipt
```

## Scale Numbers

```
100B messages/day = ~1.16M messages/second

Connection servers:
  Each server: 1M concurrent WebSocket connections
  2B users, ~500M online at peak
  Servers needed: 500M / 1M = 500 connection servers

Message queue:
  At 1.16M msg/sec, each ~1KB = ~1.16 GB/sec write throughput
  Distributed across 500 servers = ~2.3 MB/sec per server (very manageable)
  
  Messages stored for 30 days (undelivered):
  Assume 1% undelivered at any time = 1B messages × 1KB = ~1TB queue storage
```
