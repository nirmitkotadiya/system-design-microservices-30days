# Day 6: Exercises — NoSQL Databases

---

## Exercise 1: Basic Comprehension (15 minutes)

1. What is the difference between a document database and a key-value store? Give an example of data that fits each.

2. Cassandra requires queries to include the partition key. Why? What happens if you query without it?

3. Explain eventual consistency with a real-world example. When is it acceptable? When is it not?

4. A social network needs to find "friends of friends" efficiently. Why is a graph database better than SQL for this?

5. What does "schema-less" mean in the context of MongoDB? Is it truly schema-less?

---

## Exercise 2: Database Selection (25 minutes)

For each scenario, choose the best database and justify your choice:

| Scenario | Best DB | Why |
|----------|---------|-----|
| Store user sessions (expire after 30 min) | ? | ? |
| E-commerce product catalog (varied attributes per product) | ? | ? |
| IoT sensor readings (1M writes/second, query by device + time range) | ? | ? |
| Fraud detection (find unusual transaction patterns) | ? | ? |
| Banking transactions (must be ACID) | ? | ? |
| Real-time leaderboard (top 100 scores) | ? | ? |
| Content management system (articles with tags, authors) | ? | ? |
| Recommendation engine (users who bought X also bought Y) | ? | ? |

---

## Exercise 3: Document Data Modeling (30 minutes)

Design a MongoDB data model for a blogging platform:

**Requirements**:
- Users write posts
- Posts have tags
- Users can comment on posts
- Users can like posts and comments
- Users can follow other users
- Show a user's feed (posts from followed users)

**Questions**:
1. What collections would you create?
2. For each collection, show a sample document
3. What would you embed vs. reference? Justify each decision
4. What indexes would you create?
5. How would you query for a user's feed? What's the performance concern?

---

## Exercise 4: Cassandra Schema Design (25 minutes)

Design a Cassandra schema for a messaging app:

**Access patterns** (these drive the schema):
1. Get all messages in a conversation, ordered by time (most recent first)
2. Get all conversations for a user, ordered by last message time
3. Get unread message count per conversation for a user

**Rules**:
- Each query must use the partition key
- Design the schema around the queries, not the data

**Deliverable**: Write the CREATE TABLE statements with PRIMARY KEY definitions. Explain why you chose each partition key and clustering key.

---

## Exercise 5: Challenge — Polyglot Persistence (35 minutes)

### Scenario: Ride-Sharing App (like Uber)

Design the database architecture for a ride-sharing app. You are NOT limited to one database — use the right tool for each job.

**Data and access patterns**:
1. **Driver locations**: Updated every 3 seconds per driver, queried to find nearby drivers
2. **Ride history**: Users view their past rides, drivers view their earnings
3. **User profiles**: Name, payment methods, preferences
4. **Real-time matching**: Match riders to nearby available drivers
5. **Analytics**: Daily/weekly/monthly reports on rides, revenue, driver performance
6. **Surge pricing**: Calculate surge multiplier based on supply/demand in an area

**Design**:
1. For each data type, choose a database and justify
2. How do the databases interact? (e.g., when a ride completes, what gets written where?)
3. What are the consistency requirements for each? (Strong vs. eventual)
4. What's your biggest risk in this polyglot architecture?

---

## Hints

**Exercise 3**: Think about what you always access together. Comments are always shown with posts — should they be embedded? But a post could have 10,000 comments...

**Exercise 4**: For access pattern 1, the partition key should be the conversation ID. For access pattern 2, the partition key should be the user ID.

**Exercise 5**: Driver locations need geospatial queries. Redis has built-in geospatial support. Think about what needs to be fast vs. what can be eventually consistent.

---

## Self-Assessment Checklist

- [ ] I can name the four NoSQL types and give a use case for each
- [ ] I understand BASE properties and when eventual consistency is acceptable
- [ ] I can design a document model with appropriate embedding vs. referencing
- [ ] I understand why Cassandra schema design is query-driven
- [ ] I can choose the right database for a given scenario
- [ ] I understand polyglot persistence and when to use multiple databases
