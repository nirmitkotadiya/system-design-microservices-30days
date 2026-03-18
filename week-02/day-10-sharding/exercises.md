# Day 10: Exercises — Partitioning & Sharding

---

## Exercise 1: Basic Comprehension (15 minutes)

1. You have a PostgreSQL database at 80% capacity (CPU and storage). You've already added 3 read replicas. Writes are still the bottleneck. What's your next step?

2. You're sharding a `messages` table by `user_id`. A user sends a message to another user. The sender is on Shard 1, the recipient is on Shard 2. What problem does this create?

3. What is a "hot shard"? Give two different causes of hot shards.

4. You're using hash-based sharding with 4 shards. You add a 5th shard. What percentage of your data needs to move? Why is this a problem?

5. What makes a good shard key? Give an example of a bad shard key and explain why it's bad.

---

## Exercise 2: Shard Key Selection (25 minutes)

For each system, choose a shard key and justify your choice. Consider: cardinality, distribution, access patterns, and potential hot spots.

| System | Data | Access Patterns | Your Shard Key | Why |
|--------|------|-----------------|----------------|-----|
| Twitter | Tweets | Get tweets by user, get tweet by ID | ? | ? |
| Uber | Rides | Get rides by user, get rides by driver | ? | ? |
| Slack | Messages | Get messages by channel, by user | ? | ? |
| Netflix | Watch history | Get history by user | ? | ? |
| Instagram | Photos | Get photos by user, by hashtag | ? | ? |

For each, also identify: what queries become cross-shard queries with your choice?

---

## Exercise 3: Design a Sharded User Database (30 minutes)

### Scenario

Design a sharded database for a social network with:
- 1 billion users
- 10,000 writes/second (new users, profile updates)
- 1,000,000 reads/second (profile views)
- Users have: profile data, posts, followers, following

**Design**:
1. How many shards? (Assume each shard handles 2,500 writes/second)
2. What's your shard key?
3. How do you handle the "find all users in New York" query?
4. How do you handle the "get mutual friends" query?
5. A celebrity has 50M followers. Their shard is hot. How do you handle it?

---

## Exercise 4: Resharding Strategy (20 minutes)

### Scenario

You have 4 shards. Each is at 90% capacity. You need to add 4 more shards (total: 8).

**Design the migration**:
1. What data needs to move? (With simple hash sharding: `hash(key) % 4` → `hash(key) % 8`)
2. How do you migrate without downtime?
3. How do you handle writes during migration?
4. How do you verify data consistency after migration?
5. What's your rollback plan if something goes wrong?

---

## Exercise 5: Challenge — Design a Sharding Strategy for a Messaging App (35 minutes)

### Scenario: WhatsApp-like Messaging

- 2 billion users
- 100 billion messages per day
- Messages are in conversations (1:1 and group)
- Access patterns:
  - Get messages in a conversation (most common)
  - Get all conversations for a user
  - Search messages by content (rare)
  - Get unread message count per conversation

**Design**:

1. **Primary shard key**: Should you shard by `user_id` or `conversation_id`? What are the tradeoffs?

2. **Data co-location**: If you shard by `conversation_id`, how do you efficiently get all conversations for a user?

3. **Message ordering**: Messages in a conversation must be ordered by time. How does your sharding strategy affect this?

4. **Group conversations**: A group conversation with 1000 members is accessed by all 1000 members. Is this a hot shard problem?

5. **Search**: Full-text search across all messages is a cross-shard query. How would you handle this? (Hint: separate search index)

---

## Hints

**Exercise 2, Uber**: Think about what queries are most common. Riders look at their own rides. Drivers look at their own rides. But what about the matching algorithm?

**Exercise 3, Q4**: "Mutual friends" requires knowing both users' friend lists. If they're on different shards, this is a cross-shard query. How do you make it efficient?

**Exercise 5, Q2**: One approach: maintain a separate "user_conversations" table that maps user_id to conversation_ids. This can be on a different shard.

---

## Self-Assessment Checklist

- [ ] I can explain range, hash, and directory sharding with tradeoffs
- [ ] I can choose an appropriate shard key for a given system
- [ ] I understand what causes hot shards and how to prevent them
- [ ] I can describe the challenges of cross-shard queries
- [ ] I understand why resharding is complex and how to minimize data movement
- [ ] I know when sharding is necessary vs. premature
