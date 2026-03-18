# Twitter Component: Tweet Storage

## Schema Design

```sql
-- Core tweet table
CREATE TABLE tweets (
    id          BIGINT PRIMARY KEY,      -- Snowflake ID (time-sortable)
    user_id     BIGINT NOT NULL,
    content     VARCHAR(280) NOT NULL,
    created_at  TIMESTAMP NOT NULL,
    reply_to_id BIGINT,                  -- NULL for original tweets
    retweet_id  BIGINT,                  -- NULL for original tweets
    like_count  INT DEFAULT 0,
    retweet_count INT DEFAULT 0,
    reply_count INT DEFAULT 0,
    media_ids   BIGINT[],               -- Array of media IDs
    is_deleted  BOOLEAN DEFAULT FALSE
);

-- Index for user's tweets (profile page)
CREATE INDEX idx_tweets_user_created ON tweets(user_id, created_at DESC);

-- Users table
CREATE TABLE users (
    id              BIGINT PRIMARY KEY,
    username        VARCHAR(50) UNIQUE NOT NULL,
    display_name    VARCHAR(100),
    follower_count  INT DEFAULT 0,
    following_count INT DEFAULT 0,
    tweet_count     INT DEFAULT 0,
    created_at      TIMESTAMP NOT NULL
);

-- Follow relationships
CREATE TABLE follows (
    follower_id  BIGINT NOT NULL,
    followee_id  BIGINT NOT NULL,
    created_at   TIMESTAMP NOT NULL,
    PRIMARY KEY (follower_id, followee_id)
);
CREATE INDEX idx_follows_followee ON follows(followee_id);  -- "who follows me?"
```

## Snowflake IDs

Twitter invented Snowflake IDs — 64-bit integers that are:
- Globally unique (no coordination needed)
- Time-sortable (newer tweets have higher IDs)
- Embeds datacenter and machine ID

```
64-bit Snowflake ID layout:
  [41 bits: milliseconds since epoch]
  [10 bits: machine ID]
  [12 bits: sequence number]

Benefits:
  - Sort by ID = sort by time (no separate timestamp index needed)
  - Generate without central coordination
  - 4096 IDs per millisecond per machine
```

## Sharding Strategy

With 500M tweets/day, a single database can't handle the write load.

**Shard by tweet_id (hash-based)**:
```
shard = tweet_id % num_shards

Pros: Even distribution
Cons: Can't efficiently query "all tweets by user X" (scatter-gather)
```

**Shard by user_id**:
```
shard = user_id % num_shards

Pros: All tweets by a user are on one shard (efficient profile queries)
Cons: Celebrity users create hot shards
```

**Twitter's approach**: Shard by tweet_id for the main tweet store. Maintain a separate user tweet index (user_id → list of tweet_ids) for profile pages.

## Read Path Optimization

```
Timeline read:
  1. Get tweet IDs from timeline cache (Redis)
  2. Batch fetch tweet objects: GET /tweets?ids=1,2,3,4,5
  3. Fetch user objects for authors: GET /users?ids=10,11,12
  4. Assemble response

This is the "hydration" pattern:
  - Cache stores only IDs (small)
  - Fetch full objects on demand
  - Tweet objects cached separately (tweet:9999 → {content, author, ...})
```
