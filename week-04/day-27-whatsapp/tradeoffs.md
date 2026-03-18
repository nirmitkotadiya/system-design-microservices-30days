# WhatsApp Design — Tradeoffs

## Message Storage: Server vs. Client

### Server-Side Storage (iMessage, Telegram)
Messages stored on server. Accessible from any device.

**Pros**: Multi-device sync, message history after phone loss  
**Cons**: Privacy concerns, server storage costs, E2E encryption harder

### Client-Side Storage (WhatsApp's approach)
Messages stored on device. Server only holds messages until delivered.

**Pros**: Better privacy, lower server storage costs, true E2E encryption  
**Cons**: Messages lost if phone is lost, no multi-device sync (historically)

**WhatsApp's evolution**: Originally client-only. Added multi-device support in 2021 using a more complex key management scheme.

---

## Delivery Guarantees: At-Least-Once

WhatsApp uses at-least-once delivery:
- Message might be delivered multiple times (if ACK is lost)
- Client deduplicates using message ID

```
Alice sends message (ID: msg_123)
Server delivers to Bob
Bob's ACK is lost (network issue)
Server retries delivery
Bob receives msg_123 again
Bob's client: "Already have msg_123, ignore duplicate"
```

**Why not exactly-once?** Exactly-once requires distributed coordination, which adds latency. At-least-once with client deduplication is simpler and faster.

---

## Presence: Accuracy vs. Privacy

### Accurate Presence
Show exact online/offline status and last seen time.

**Pros**: Users know when friends are available  
**Cons**: Privacy concern — stalkers can track when you're online

### Privacy-First Presence
Allow users to hide last seen, hide online status.

**WhatsApp's approach**: User-controlled privacy settings
- "Everyone" can see last seen
- "My Contacts" can see last seen
- "Nobody" can see last seen

**Tradeoff**: If you hide your last seen, you can't see others' last seen.

---

## Group Encryption: Individual Keys vs. Group Key

### Individual Keys (WhatsApp's approach for small groups)
Each message encrypted separately for each recipient.

**Pros**: True E2E encryption, server can't read messages  
**Cons**: Sender must encrypt N times for N recipients

### Group Key
One key shared among all group members.

**Pros**: Efficient (encrypt once)  
**Cons**: If one member's device is compromised, all messages are exposed. Key rotation when members leave is complex.

**WhatsApp's approach**: 
- Small groups: individual keys (Sender Key protocol)
- Large groups: Sender Key (one encryption, distributed to all members)

---

## The 100 Billion Messages/Day Challenge

WhatsApp handles 100B messages/day with only ~50 engineers (at acquisition in 2014).

**How?**
1. **Erlang**: WhatsApp uses Erlang, designed for telecom systems. Handles millions of concurrent connections efficiently.
2. **Minimal server-side processing**: Messages are just routed, not processed. No ML, no ads, no complex logic.
3. **Client-side encryption**: Server doesn't need to encrypt/decrypt.
4. **Simple data model**: Messages are just bytes to the server.

**Lesson**: Simplicity scales. WhatsApp's architecture is simple by design.
