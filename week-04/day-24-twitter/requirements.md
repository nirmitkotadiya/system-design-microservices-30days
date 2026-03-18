# Twitter/X System Design — Requirements

## Functional Requirements

### Core Features
1. Users can post tweets (280 characters, with optional media)
2. Users can follow other users
3. Users see a home timeline (tweets from followed users)
4. Users can like, retweet, and reply to tweets
5. Users can search tweets and users
6. Trending topics (real-time)
7. Direct messages (1:1 and group)
8. Notifications (likes, retweets, follows, mentions)

### Scale Requirements (Twitter's actual scale)
- 500 million registered users
- 200 million daily active users
- 500 million tweets per day (~6,000 tweets/second)
- 300 billion timeline reads per day (~3.5 million reads/second)
- Read:write ratio = 600:1

## Non-Functional Requirements

| Requirement | Target |
|-------------|--------|
| Timeline load latency | < 200ms (p99) |
| Tweet post latency | < 500ms |
| Search latency | < 1 second |
| Availability | 99.99% |
| Consistency | Eventual (timeline can be slightly stale) |
| Durability | No tweet loss |

## Out of Scope (for this design)
- Ads system
- Spaces (audio rooms)
- Twitter Blue features
- Content moderation at scale
