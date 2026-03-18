# Day 6: NoSQL Databases — Concepts Deep Dive

## 1. Why NoSQL?

SQL databases are excellent but have limitations at extreme scale:

| Problem | SQL Limitation | NoSQL Solution |
|---------|---------------|----------------|
| Flexible schema | Schema changes require migrations | Schema-less documents |
| Horizontal write scaling | Sharding is complex | Built-in distribution |
| Specific access patterns | Joins are expensive | Denormalized for your query |
| Massive scale | Single-machine limits | Designed for clusters |
| High write throughput | ACID overhead | Eventual consistency |

**Important**: NoSQL doesn't mean "no SQL" or "no structure." It means "not only SQL." Many NoSQL databases have query languages, and some even support SQL-like syntax.

---

## 2. BASE vs. ACID

NoSQL databases often trade ACID guarantees for performance and availability.

**BASE** (the NoSQL alternative to ACID):
- **B**asically **A**vailable: The system guarantees availability (per CAP theorem)
- **S**oft state: State may change over time even without input (due to eventual consistency)
- **E**ventually consistent: The system will become consistent over time

```
ACID: "The data is always correct."
BASE: "The data will eventually be correct."

Example (BASE):
- User A updates their profile picture
- User B sees the old picture for 2 seconds
- After 2 seconds, User B sees the new picture
- This is "eventually consistent" — acceptable for profile pictures
```

**When eventual consistency is NOT acceptable**:
- Bank transfers (money must be consistent immediately)
- Inventory management (can't oversell)
- Ticket booking (can't double-book)

---

## 3. Type 1: Key-Value Stores

**Examples**: Redis, DynamoDB, Memcached, Riak

**Data model**: Simple key → value pairs. Value can be anything (string, JSON, binary).

```
"user:123" → {"name": "Alice", "email": "alice@example.com"}
"session:abc" → {"user_id": 123, "expires": 1700000000}
"counter:page_views" → 1000000
```

**Strengths**:
- Extremely fast (O(1) lookups)
- Simple to scale horizontally
- Great for caching, sessions, counters

**Weaknesses**:
- Can only look up by key (no queries on values)
- No relationships between data
- Limited data modeling

**Best for**:
- Session storage
- Caching
- Rate limiting counters
- Feature flags
- Leaderboards (Redis sorted sets)

**Real-world example**: Amazon DynamoDB stores shopping cart data. The key is `user_id`, the value is the cart contents. Fast lookup, simple structure.

---

## 4. Type 2: Document Databases

**Examples**: MongoDB, CouchDB, Firestore, DynamoDB (also document)

**Data model**: JSON-like documents, grouped into collections.

```json
// users collection
{
  "_id": "user_123",
  "name": "Alice Smith",
  "email": "alice@example.com",
  "addresses": [
    {"type": "home", "street": "123 Main St", "city": "Boston"},
    {"type": "work", "street": "456 Office Ave", "city": "Boston"}
  ],
  "preferences": {
    "theme": "dark",
    "notifications": true
  }
}
```

**Strengths**:
- Flexible schema (add fields without migrations)
- Natural fit for hierarchical data
- Good for read-heavy workloads with denormalized data
- Easy to scale reads

**Weaknesses**:
- No joins (must denormalize or do multiple queries)
- Eventual consistency by default
- Harder to maintain data integrity

**Best for**:
- Content management systems
- User profiles
- Product catalogs
- Event logging

**Data modeling tip**: In document databases, embed data that you always access together. Reference data that you access independently.

```json
// EMBED: Order always needs its items
{
  "_id": "order_456",
  "user_id": "user_123",
  "items": [
    {"product_id": "prod_1", "name": "Widget", "price": 9.99, "qty": 2},
    {"product_id": "prod_2", "name": "Gadget", "price": 24.99, "qty": 1}
  ],
  "total": 44.97
}

// REFERENCE: User profile is accessed independently
{
  "_id": "order_456",
  "user_id": "user_123",  // Reference, not embedded
  "items": [...]
}
```

---

## 5. Type 3: Column-Family Stores (Wide-Column)

**Examples**: Apache Cassandra, HBase, Google Bigtable

**Data model**: Rows with dynamic columns, organized by partition key.

```
Partition Key: user_id
Row Key: timestamp

user_id | 2024-01-01 | 2024-01-02 | 2024-01-03
--------|------------|------------|------------
user_1  | {steps:5k} | {steps:7k} | {steps:6k}
user_2  | {steps:3k} |            | {steps:8k}
```

**Cassandra's key insight**: Data is partitioned by a partition key and sorted by a clustering key. Queries must include the partition key.

```sql
-- Cassandra CQL
CREATE TABLE user_activity (
    user_id UUID,
    event_time TIMESTAMP,
    event_type TEXT,
    data TEXT,
    PRIMARY KEY (user_id, event_time)  -- user_id is partition key
) WITH CLUSTERING ORDER BY (event_time DESC);

-- Fast: includes partition key
SELECT * FROM user_activity WHERE user_id = ? AND event_time > ?;

-- SLOW/FORBIDDEN: no partition key
SELECT * FROM user_activity WHERE event_type = 'login';
```

**Strengths**:
- Extremely high write throughput (append-only writes)
- Excellent for time-series data
- Linear horizontal scalability
- No single point of failure

**Weaknesses**:
- Must design schema around your queries
- No joins
- Eventual consistency
- Complex data modeling

**Best for**:
- Time-series data (IoT sensors, metrics, logs)
- Activity feeds
- Messaging systems
- Any write-heavy, time-ordered data

> **DDIA Reference**: Chapter 3 covers LSM-trees and SSTables, which are the storage engine behind Cassandra and HBase.

---

## 6. Type 4: Graph Databases

**Examples**: Neo4j, Amazon Neptune, JanusGraph

**Data model**: Nodes (entities) and edges (relationships).

```
(Alice)-[:FOLLOWS]->(Bob)
(Alice)-[:LIKES]->(Post:123)
(Bob)-[:AUTHORED]->(Post:123)
(Post:123)-[:TAGGED]->(Topic:Python)
```

**Strengths**:
- Natural fit for highly connected data
- Efficient traversal of relationships
- Flexible schema

**Weaknesses**:
- Not good for non-graph queries
- Harder to scale horizontally
- Niche use cases

**Best for**:
- Social networks (friend-of-friend queries)
- Recommendation engines
- Fraud detection (unusual connection patterns)
- Knowledge graphs

**Real-world example**: LinkedIn uses graph databases to power "People You May Know." Finding friends-of-friends in a relational database requires expensive recursive joins. In a graph database, it's a simple traversal.

---

## 7. Choosing the Right Database

Use this decision tree:

```
Is your data highly connected (social graph, recommendations)?
  YES → Graph database (Neo4j)
  NO ↓

Do you need complex queries, joins, and ACID transactions?
  YES → SQL (PostgreSQL, MySQL)
  NO ↓

Is your primary access pattern key-based lookup?
  YES → Key-value store (Redis, DynamoDB)
  NO ↓

Is your data time-series or write-heavy with known query patterns?
  YES → Column store (Cassandra)
  NO ↓

Do you have flexible/hierarchical data with varied structure?
  YES → Document store (MongoDB)
  NO → SQL (default choice)
```

### Real-World Database Choices

| Company | Use Case | Database | Why |
|---------|----------|----------|-----|
| Instagram | User posts | PostgreSQL | ACID, complex queries |
| Instagram | Feed cache | Redis | Fast key-value lookup |
| Netflix | User preferences | Cassandra | High write throughput, global scale |
| LinkedIn | Social graph | Graph DB | Relationship traversal |
| Airbnb | Listings | PostgreSQL | Complex search queries |
| Uber | Driver locations | Redis (geospatial) | Fast geo queries |

---

## 8. Common Pitfalls

### Using MongoDB for Everything
MongoDB is flexible, but that flexibility can lead to inconsistent data. Use SQL when you need data integrity.

### Ignoring Access Patterns
In Cassandra, you must design your schema around your queries. Designing the schema first and queries second leads to full table scans.

### Assuming NoSQL = Scale
NoSQL databases can scale, but they require careful design. A poorly designed Cassandra schema can be slower than PostgreSQL.

### Forgetting About Eventual Consistency
If your application requires strong consistency (banking, inventory), eventual consistency will cause bugs.

---

## References
- DDIA Chapter 2: Data Models and Query Languages
- DDIA Chapter 3: Storage and Retrieval (LSM-trees for Cassandra)
- [MongoDB Data Modeling Guide](https://www.mongodb.com/docs/manual/data-modeling/)
- [Cassandra Data Modeling](https://cassandra.apache.org/doc/latest/cassandra/data_modeling/)
