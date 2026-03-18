# Day 9: Exercises — Replication Strategies

---

## Exercise 1: Basic Comprehension (15 minutes)

1. What is replication lag? Give a real-world scenario where it causes a visible bug.

2. You have N=5 replicas. You set W=3, R=3. Does W+R > N? What consistency guarantee does this give you?

3. What is "split brain" in the context of leader election? How do fencing tokens prevent it?

4. Explain the difference between synchronous and asynchronous replication. What does each sacrifice?

5. A user posts a tweet. They immediately refresh their feed and don't see it. What replication issue caused this? How would you fix it?

---

## Exercise 2: Quorum Math (20 minutes)

For each configuration (N, W, R), determine:
- Does W + R > N? (strong consistency guarantee?)
- What's the maximum number of node failures that can be tolerated for writes?
- What's the maximum number of node failures that can be tolerated for reads?

| N | W | R | W+R>N? | Write fault tolerance | Read fault tolerance |
|---|---|---|--------|----------------------|---------------------|
| 3 | 2 | 2 | ? | ? | ? |
| 5 | 3 | 3 | ? | ? | ? |
| 5 | 1 | 1 | ? | ? | ? |
| 5 | 5 | 1 | ? | ? | ? |
| 7 | 4 | 4 | ? | ? | ? |

For each row, describe the tradeoff (what do you gain and lose?).

---

## Exercise 3: Design a High-Availability Database (25 minutes)

### Scenario

Design a PostgreSQL setup for a financial application:
- 10,000 writes/second
- 100,000 reads/second
- Must survive the failure of any single node without data loss
- Recovery time objective (RTO): < 30 seconds
- Recovery point objective (RPO): 0 (no data loss)

**Design**:
1. How many nodes? What are their roles?
2. Synchronous or asynchronous replication? Why?
3. How do you detect leader failure?
4. How do you promote a follower to leader?
5. How do you route reads vs. writes?
6. What happens to in-flight transactions when the leader fails?

Draw the architecture diagram.

---

## Exercise 4: Conflict Resolution (20 minutes)

### Scenario: Collaborative Note-Taking App

Two users edit the same note simultaneously:
- User A (connected to DC East): changes title to "Meeting Notes"
- User B (connected to DC West): changes title to "Q4 Planning"

Both writes succeed locally. When the DCs sync, there's a conflict.

**Evaluate each resolution strategy**:

1. **Last Write Wins**: User A's write was at t=1000ms, User B's at t=1001ms. What's the result? What's the problem?

2. **User-defined merge**: The app shows both versions and asks the user to choose. What's the UX problem?

3. **Operational Transformation** (Google Docs approach): Track the operations, not just the final state. How would this work for a title change?

4. **CRDT approach**: Design a data structure for a "title" field that can be merged without conflicts. (Hint: think about what information you need to resolve conflicts deterministically.)

Which approach would you use for a collaborative note-taking app? Why?

---

## Exercise 5: Challenge — Design a Multi-Region Database (35 minutes)

### Scenario

You're building a global e-commerce platform:
- Users in North America, Europe, Asia-Pacific
- Users must see their own orders immediately after placing them
- Users don't need to see other users' orders in real-time
- Orders must never be lost
- The system must be available even if one region goes down

**Design the replication strategy**:

1. **Topology**: Single leader? Multi-leader? Leaderless? One per region?

2. **Consistency**: What consistency level for order placement? For order history reads?

3. **Conflict avoidance**: How do you design the system to minimize conflicts? (Hint: can you ensure each user's data is only written in one region?)

4. **Failover**: If the NA region goes down, what happens to NA users? Can they still place orders?

5. **Data residency**: European regulations require EU user data to stay in EU. How does this affect your design?

---

## Hints

**Exercise 2**: Write fault tolerance = N - W (you can lose this many nodes and still write). Read fault tolerance = N - R.

**Exercise 3**: RPO = 0 means no data loss. This requires synchronous replication to at least one follower.

**Exercise 5**: Think about "user affinity" — routing each user's writes to a specific region. This avoids most conflicts.

---

## Self-Assessment Checklist

- [ ] I can explain leader-follower, multi-leader, and leaderless replication
- [ ] I understand the W+R>N quorum formula
- [ ] I can identify replication lag issues in application code
- [ ] I can design a high-availability database setup
- [ ] I understand conflict resolution strategies for multi-leader replication
- [ ] I know what split-brain is and how to prevent it
