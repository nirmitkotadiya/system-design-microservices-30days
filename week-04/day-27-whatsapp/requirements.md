# WhatsApp System Design — Requirements

## Functional Requirements

1. 1:1 messaging (text, images, video, audio, documents)
2. Group messaging (up to 1,024 members)
3. Message delivery receipts (sent ✓, delivered ✓✓, read ✓✓ blue)
4. Online/offline presence
5. End-to-end encryption
6. Voice and video calls
7. Message history (stored on device, not server)
8. Push notifications for offline users

## Scale Requirements (WhatsApp's actual scale)
- 2 billion users
- 100 billion messages per day
- 2 billion minutes of voice/video calls per day
- 1 billion groups
- 5 million servers (at peak)

## Non-Functional Requirements

| Requirement | Target |
|-------------|--------|
| Message delivery latency | < 100ms (online users) |
| Message delivery (offline) | Within 30 days |
| Availability | 99.99% |
| End-to-end encryption | All messages |
| Message ordering | Guaranteed within conversation |

## Key Technical Challenges
1. Message delivery guarantees (at-least-once, in-order)
2. Presence system (2B users, online/offline status)
3. End-to-end encryption at scale
4. Group messaging fan-out (1,024 members)
5. Offline message storage and delivery
