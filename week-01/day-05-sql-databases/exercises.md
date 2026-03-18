# Day 5: Exercises — SQL Databases Deep Dive

---

## Exercise 1: Basic Comprehension (15 minutes)

1. A bank transfer fails halfway through (debit succeeds, credit fails). Which ACID property prevents this from leaving the database in an inconsistent state?

2. You have a `users` table with 10 million rows. A query `SELECT * FROM users WHERE email = 'alice@example.com'` takes 5 seconds. What's the likely cause and fix?

3. What is the "leftmost prefix rule" for composite indexes? Give an example of a query that would and wouldn't use the index `(last_name, first_name)`.

4. Explain the difference between `READ COMMITTED` and `REPEATABLE READ` isolation levels. Give a scenario where the difference matters.

5. Your app opens a new database connection for every HTTP request. You have 1000 concurrent users. What problem does this cause?

---

## Exercise 2: Schema Design (30 minutes)

Design a normalized database schema for a simplified e-commerce platform:

**Requirements**:
- Users can have multiple addresses (shipping, billing)
- Products belong to categories (can be in multiple categories)
- Orders contain multiple products with quantities
- Orders have a status (pending, paid, shipped, delivered)
- Products have inventory tracked per warehouse

**Deliverable**: Write the CREATE TABLE statements with:
- Primary keys
- Foreign keys
- Appropriate data types
- At least 3 indexes (justify each)
- At least 1 constraint (CHECK, UNIQUE, etc.)

---

## Exercise 3: Query Optimization (25 minutes)

Given this schema:
```sql
CREATE TABLE posts (
    id BIGINT PRIMARY KEY,
    user_id BIGINT,
    content TEXT,
    created_at TIMESTAMP,
    like_count INT DEFAULT 0,
    is_deleted BOOLEAN DEFAULT FALSE
);

CREATE TABLE follows (
    follower_id BIGINT,
    followee_id BIGINT,
    PRIMARY KEY (follower_id, followee_id)
);
```

**Optimize these queries**:

1. Get the 20 most recent posts from users that user #123 follows:
```sql
-- Current (slow) version:
SELECT p.* FROM posts p
WHERE p.user_id IN (
    SELECT followee_id FROM follows WHERE follower_id = 123
)
AND p.is_deleted = FALSE
ORDER BY p.created_at DESC
LIMIT 20;
```
What indexes would you add? Can you rewrite the query to be faster?

2. Get the top 10 most-liked posts from the last 7 days:
```sql
SELECT * FROM posts
WHERE created_at > NOW() - INTERVAL '7 days'
AND is_deleted = FALSE
ORDER BY like_count DESC
LIMIT 10;
```
What index would help here?

---

## Exercise 4: ACID in Practice (20 minutes)

### Scenario: Ticket Booking System

A concert has 100 tickets. Two users try to buy the last ticket simultaneously.

```python
# User A and User B both run this code at the same time:
def buy_ticket(user_id, event_id):
    available = db.query(
        "SELECT available_count FROM events WHERE id = ?", event_id
    )
    if available > 0:
        db.execute(
            "UPDATE events SET available_count = available_count - 1 WHERE id = ?",
            event_id
        )
        db.execute(
            "INSERT INTO tickets (user_id, event_id) VALUES (?, ?)",
            user_id, event_id
        )
        return "Ticket purchased!"
    return "Sold out"
```

**Questions**:
1. What race condition exists in this code?
2. How would you fix it using pessimistic locking?
3. How would you fix it using optimistic locking?
4. Which approach is better for a high-traffic ticket sale (like Taylor Swift tickets)?

---

## Exercise 5: Challenge — Design a Scalable Read Layer (35 minutes)

### Scenario

Your PostgreSQL database handles:
- 10,000 writes/second
- 100,000 reads/second
- 500GB of data
- p99 read latency: 200ms (too slow, target is 50ms)

**Design a solution**:

1. **Read replicas**: How many do you need? How do you route reads vs. writes?

2. **Caching layer**: What do you cache? What's the cache key structure? What TTL?

3. **Index optimization**: The slow queries are all on `posts` table filtering by `user_id` and `created_at`. What index would you add?

4. **Connection pooling**: You have 50 app servers, each wanting 20 connections. That's 1000 connections to PostgreSQL. How do you handle this?

5. **Read-your-writes consistency**: After a user posts something, they should see it immediately. But with read replicas, they might read from a replica that hasn't caught up. How do you solve this?

---

## Hints

**Exercise 2**: Think about the many-to-many relationship between products and categories. You'll need a junction table.

**Exercise 3, Q1**: The subquery runs once per row. A JOIN would be more efficient. Also think about what index would help the ORDER BY.

**Exercise 4**: The race condition is a classic "check-then-act" problem. Both users check `available > 0` before either updates.

**Exercise 5, Q5**: One approach: route reads to primary for a short window after a write from that user.

---

## Self-Assessment Checklist

- [ ] I can explain all four ACID properties with examples
- [ ] I can design a normalized schema for a given domain
- [ ] I understand how B-tree indexes work and when to use them
- [ ] I can identify and fix the N+1 query problem
- [ ] I understand the race condition in the ticket booking example
- [ ] I know how to scale PostgreSQL with read replicas and connection pooling
