# Day 5: SQL Databases — Concepts Deep Dive

## 1. ACID Properties

ACID is the set of guarantees that make relational databases trustworthy for critical data.

### Atomicity
**"All or nothing."**

A transaction either completes fully or not at all. No partial updates.

```sql
-- Transfer $100 from Alice to Bob
BEGIN;
  UPDATE accounts SET balance = balance - 100 WHERE user_id = 'alice';
  UPDATE accounts SET balance = balance + 100 WHERE user_id = 'bob';
COMMIT;
-- If the second UPDATE fails, the first is rolled back automatically
```

Without atomicity: Alice loses $100 but Bob never receives it.

### Consistency
**"The database moves from one valid state to another."**

All constraints, rules, and triggers are enforced. A transaction that would violate a constraint is rejected.

```sql
-- This fails if alice's balance would go negative (CHECK constraint)
ALTER TABLE accounts ADD CONSTRAINT positive_balance CHECK (balance >= 0);
```

### Isolation
**"Concurrent transactions don't interfere with each other."**

Each transaction sees a consistent snapshot of the database, as if it were the only transaction running.

```
Without isolation:
T1: Read balance = $100
T2: Read balance = $100
T1: Write balance = $0 (withdrew $100)
T2: Write balance = $0 (withdrew $100)
Result: $200 withdrawn from $100 account!

With isolation (serializable):
T1: Read balance = $100, Write balance = $0
T2: Read balance = $0 → Rejected (insufficient funds)
```

**Isolation Levels** (weakest to strongest):

| Level | Dirty Read | Non-Repeatable Read | Phantom Read |
|-------|-----------|---------------------|--------------|
| Read Uncommitted | Possible | Possible | Possible |
| Read Committed | Prevented | Possible | Possible |
| Repeatable Read | Prevented | Prevented | Possible |
| Serializable | Prevented | Prevented | Prevented |

Most databases default to Read Committed. PostgreSQL uses Repeatable Read for its default transaction isolation.

> **DDIA Reference**: Chapter 7 covers isolation levels in exhaustive detail. This is one of the most important chapters in the book.

### Durability
**"Committed data survives crashes."**

Once a transaction is committed, it's written to disk (via WAL — Write-Ahead Log). A power failure won't lose committed data.

```
WAL (Write-Ahead Log):
1. Write transaction to WAL (sequential, fast)
2. Acknowledge commit to client
3. Apply changes to data files (background)

If crash occurs after step 2: WAL is replayed on restart
```

---

## 2. How Indexes Work

An index is a separate data structure that allows the database to find rows without scanning the entire table.

### Without an Index (Full Table Scan)
```sql
SELECT * FROM users WHERE email = 'alice@example.com';
-- Database reads EVERY row and checks if email matches
-- O(n) — gets slower as table grows
```

### With a B-Tree Index
```sql
CREATE INDEX idx_users_email ON users(email);
SELECT * FROM users WHERE email = 'alice@example.com';
-- Database traverses B-tree to find the row directly
-- O(log n) — stays fast even with millions of rows
```

### B-Tree Structure (Simplified)
```
                    [M]
                   /   \
              [D,H]     [R,V]
             / | \      / | \
           [A][E][I]  [N][S][W]
           
Finding 'E':
1. Compare 'E' with 'M' → go left
2. Compare 'E' with 'D','H' → between D and H
3. Find 'E' in leaf node
Total: 3 comparisons for any value in the tree
```

### Types of Indexes

**B-Tree Index** (default)
- Good for: equality (`=`), range (`>`, `<`, `BETWEEN`), sorting (`ORDER BY`)
- Not good for: full-text search, geometric data

**Hash Index**
- Good for: equality only (`=`)
- Not good for: range queries
- Faster than B-tree for equality, but limited

**Composite Index**
```sql
CREATE INDEX idx_users_name ON users(last_name, first_name);
-- Efficient for: WHERE last_name = 'Smith'
-- Efficient for: WHERE last_name = 'Smith' AND first_name = 'John'
-- NOT efficient for: WHERE first_name = 'John' (leftmost prefix rule)
```

**Covering Index**
```sql
-- Query only needs id and email
SELECT id, email FROM users WHERE email = 'alice@example.com';

-- Covering index includes all needed columns
CREATE INDEX idx_users_email_covering ON users(email) INCLUDE (id);
-- Database never touches the main table — all data in the index
```

### Index Tradeoffs

| Benefit | Cost |
|---------|------|
| Faster reads | Slower writes (index must be updated) |
| Faster sorts | More disk space |
| Faster joins | More memory for index pages |

**Rule of thumb**: Index columns that appear in WHERE, JOIN ON, and ORDER BY clauses. Don't over-index write-heavy tables.

---

## 3. Query Optimization

### The Query Planner
The database doesn't execute your SQL literally. It creates an execution plan — the most efficient way to get the result.

```sql
EXPLAIN ANALYZE SELECT * FROM orders 
WHERE user_id = 123 AND status = 'pending'
ORDER BY created_at DESC;
```

```
QUERY PLAN:
Sort (cost=150.25..152.75 rows=1000)
  -> Index Scan using idx_orders_user_id on orders
       Index Cond: (user_id = 123)
       Filter: (status = 'pending')
```

Reading an execution plan:
- **Seq Scan**: Full table scan — usually bad for large tables
- **Index Scan**: Using an index — good
- **Index Only Scan**: Covering index — best
- **Hash Join**: Joining tables using a hash table
- **Nested Loop**: Joining tables with nested iteration — can be slow

### The N+1 Query Problem

```python
# BAD: N+1 queries
users = db.query("SELECT * FROM users LIMIT 100")  # 1 query
for user in users:
    orders = db.query(f"SELECT * FROM orders WHERE user_id = {user.id}")  # 100 queries!
# Total: 101 queries

# GOOD: 1 query with JOIN
results = db.query("""
    SELECT u.*, o.*
    FROM users u
    LEFT JOIN orders o ON o.user_id = u.id
    LIMIT 100
""")  # 1 query
```

The N+1 problem is one of the most common performance issues in web applications.

---

## 4. Transactions and Locking

### Optimistic vs. Pessimistic Locking

**Pessimistic Locking**: Lock the row before reading it.
```sql
BEGIN;
SELECT * FROM accounts WHERE id = 1 FOR UPDATE;  -- Locks the row
UPDATE accounts SET balance = balance - 100 WHERE id = 1;
COMMIT;
```
Good for: High contention scenarios where conflicts are likely.

**Optimistic Locking**: Read without locking, check for conflicts on write.
```sql
-- Read with version number
SELECT id, balance, version FROM accounts WHERE id = 1;
-- Returns: {id: 1, balance: 500, version: 3}

-- Update only if version hasn't changed
UPDATE accounts 
SET balance = 400, version = 4 
WHERE id = 1 AND version = 3;
-- If 0 rows updated, someone else modified it — retry
```
Good for: Low contention scenarios where conflicts are rare.

---

## 5. Scaling SQL Databases

### Read Replicas
```
                    ┌─────────────────┐
Writes ────────────▶│  Primary DB     │
                    └────────┬────────┘
                             │ Replication
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
        ┌──────────┐  ┌──────────┐  ┌──────────┐
Reads ─▶│ Replica 1│  │ Replica 2│  │ Replica 3│
        └──────────┘  └──────────┘  └──────────┘
```

- Replicas handle read traffic (typically 80-90% of queries)
- Replication lag: replicas may be slightly behind primary
- Use for: analytics queries, reporting, read-heavy workloads

### Connection Pooling
Opening a new database connection is expensive (~50ms). Connection pools reuse connections.

```python
# Without pooling: new connection per request
def get_user(user_id):
    conn = psycopg2.connect(...)  # 50ms to establish
    result = conn.execute("SELECT * FROM users WHERE id = ?", user_id)
    conn.close()
    return result

# With pooling: reuse existing connections
pool = psycopg2.pool.ThreadedConnectionPool(minconn=5, maxconn=20, ...)

def get_user(user_id):
    conn = pool.getconn()  # ~0.1ms to get from pool
    result = conn.execute("SELECT * FROM users WHERE id = ?", user_id)
    pool.putconn(conn)
    return result
```

**PgBouncer**: A dedicated connection pooler for PostgreSQL. Handles thousands of app connections with a small number of actual DB connections.

### Vertical Scaling
Before sharding, try:
- More RAM (larger buffer pool = more data in memory)
- Faster SSDs (NVMe vs. SATA)
- More CPU cores (for parallel query execution)

### When to Shard
Sharding (splitting data across multiple databases) is complex. Only do it when:
- Single database can't handle write throughput
- Dataset is too large for one machine
- You've exhausted vertical scaling options

We'll cover sharding in depth on Day 10.

---

## 6. Schema Design Best Practices

### Normalization
Organize data to reduce redundancy:

```sql
-- BAD: Denormalized (redundant data)
CREATE TABLE orders (
    id INT,
    user_name VARCHAR(100),    -- Duplicated for every order
    user_email VARCHAR(100),   -- Duplicated for every order
    product_name VARCHAR(100), -- Duplicated for every order
    quantity INT,
    price DECIMAL
);

-- GOOD: Normalized (3NF)
CREATE TABLE users (id INT PRIMARY KEY, name VARCHAR(100), email VARCHAR(100));
CREATE TABLE products (id INT PRIMARY KEY, name VARCHAR(100), price DECIMAL);
CREATE TABLE orders (
    id INT PRIMARY KEY,
    user_id INT REFERENCES users(id),
    product_id INT REFERENCES products(id),
    quantity INT,
    created_at TIMESTAMP
);
```

### When to Denormalize
Normalization is great for writes. But for reads, joins are expensive. Sometimes denormalization is the right tradeoff:

```sql
-- For a read-heavy analytics table, denormalize for query speed
CREATE TABLE order_analytics (
    order_id INT,
    user_name VARCHAR(100),  -- Denormalized
    product_name VARCHAR(100),  -- Denormalized
    total_price DECIMAL,
    created_at TIMESTAMP
);
```

---

## References
- DDIA Chapters 2–3: Data Models and Storage Engines
- [PostgreSQL Documentation: Query Planning](https://www.postgresql.org/docs/current/performance-tips.html)
- [Use the Index, Luke](https://use-the-index-luke.com/) — Free book on SQL indexing
