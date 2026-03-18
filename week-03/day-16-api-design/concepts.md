# Day 16: API Design — Concepts Deep Dive

## 1. REST Principles

REST (Representational State Transfer) is an architectural style, not a protocol.

### The 6 REST Constraints

1. **Client-Server**: Separation of concerns between UI and data storage
2. **Stateless**: Each request contains all information needed; no server-side session
3. **Cacheable**: Responses must define themselves as cacheable or non-cacheable
4. **Uniform Interface**: Consistent interface across all resources
5. **Layered System**: Client doesn't know if it's talking to the actual server or a proxy
6. **Code on Demand** (optional): Server can send executable code to client

### Resource-Oriented Design

REST is about resources, not actions:

```
BAD (action-oriented, RPC-style):
  POST /createUser
  POST /deleteUser?id=123
  POST /getUserById?id=123
  POST /updateUserEmail

GOOD (resource-oriented, REST):
  POST   /users          → Create user
  DELETE /users/123      → Delete user
  GET    /users/123      → Get user
  PATCH  /users/123      → Update user (partial)
  PUT    /users/123      → Replace user (full)
```

### HTTP Methods

| Method | Purpose | Idempotent? | Safe? |
|--------|---------|-------------|-------|
| GET | Read resource | Yes | Yes |
| POST | Create resource | No | No |
| PUT | Replace resource | Yes | No |
| PATCH | Partial update | No | No |
| DELETE | Delete resource | Yes | No |

**Idempotent**: Calling it multiple times has the same effect as calling it once.  
**Safe**: Doesn't modify server state.

---

## 2. URL Design Best Practices

```
# Use nouns, not verbs
GET /users/123          ✓
GET /getUser/123        ✗

# Use plural nouns
GET /users              ✓
GET /user               ✗

# Nested resources for relationships
GET /users/123/orders   ✓ (orders belonging to user 123)
GET /orders?user_id=123 ✓ (also acceptable)

# Use kebab-case for multi-word resources
GET /user-profiles      ✓
GET /userProfiles       ✗
GET /user_profiles      ✗ (acceptable but less common)

# Don't include file extensions
GET /users/123          ✓
GET /users/123.json     ✗

# Version in URL (one approach)
GET /v1/users/123       ✓
```

---

## 3. Request and Response Design

### Request Body (POST/PUT/PATCH)
```json
POST /users
{
  "name": "Alice Smith",
  "email": "alice@example.com",
  "role": "admin"
}
```

### Response Body
```json
HTTP/1.1 201 Created
Location: /users/123

{
  "id": "123",
  "name": "Alice Smith",
  "email": "alice@example.com",
  "role": "admin",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

### Error Responses
```json
HTTP/1.1 422 Unprocessable Entity

{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed",
    "details": [
      {
        "field": "email",
        "message": "Invalid email format"
      },
      {
        "field": "name",
        "message": "Name must be at least 2 characters"
      }
    ]
  }
}
```

---

## 4. Pagination

Never return unbounded lists. Always paginate.

### Offset Pagination
```
GET /posts?offset=0&limit=20    → Posts 1-20
GET /posts?offset=20&limit=20   → Posts 21-40
GET /posts?offset=40&limit=20   → Posts 41-60
```

**Response**:
```json
{
  "data": [...],
  "pagination": {
    "total": 1000,
    "offset": 0,
    "limit": 20,
    "next": "/posts?offset=20&limit=20",
    "prev": null
  }
}
```

**Problem**: If items are inserted/deleted between pages, you get duplicates or skip items.

### Cursor Pagination (Better)
```
GET /posts?limit=20                    → First 20 posts
GET /posts?cursor=eyJpZCI6MjB9&limit=20 → Next 20 posts
```

**Response**:
```json
{
  "data": [...],
  "pagination": {
    "next_cursor": "eyJpZCI6NDB9",
    "has_more": true
  }
}
```

**Pros**: Stable pagination even with inserts/deletes. Works well with infinite scroll.  
**Cons**: Can't jump to page 5 directly.

---

## 5. Filtering, Sorting, and Searching

```
# Filtering
GET /posts?status=published&author_id=123

# Sorting
GET /posts?sort=created_at&order=desc
GET /posts?sort=-created_at  (minus = descending)

# Searching
GET /posts?q=system+design

# Field selection (reduce response size)
GET /users?fields=id,name,email

# Combining
GET /posts?status=published&sort=-created_at&limit=20
```

---

## 6. API Versioning

### Option 1: URL Versioning
```
GET /v1/users/123
GET /v2/users/123
```
**Pros**: Explicit, easy to route  
**Cons**: URL pollution, clients must update URLs

### Option 2: Header Versioning
```
GET /users/123
Accept: application/vnd.myapi.v2+json
```
**Pros**: Clean URLs  
**Cons**: Less visible, harder to test in browser

### Option 3: Query Parameter
```
GET /users/123?version=2
```
**Pros**: Easy to test  
**Cons**: Pollutes query string

### Breaking vs. Non-Breaking Changes

**Non-breaking** (safe to deploy without version bump):
- Adding new optional fields to response
- Adding new optional request parameters
- Adding new endpoints

**Breaking** (requires new version):
- Removing fields from response
- Changing field types
- Changing URL structure
- Changing authentication method

---

## 7. gRPC

gRPC is a high-performance RPC framework using Protocol Buffers (protobuf) for serialization.

### Why gRPC?

| Feature | REST/JSON | gRPC/Protobuf |
|---------|-----------|---------------|
| Serialization | JSON (text) | Binary (protobuf) |
| Performance | Slower | 5-10x faster |
| Schema | Optional (OpenAPI) | Required (.proto) |
| Streaming | Limited | Native support |
| Browser support | Native | Requires proxy |
| Human readable | Yes | No |

### gRPC Service Definition
```protobuf
// user.proto
syntax = "proto3";

service UserService {
  rpc GetUser (GetUserRequest) returns (User);
  rpc CreateUser (CreateUserRequest) returns (User);
  rpc ListUsers (ListUsersRequest) returns (stream User);  // Server streaming
}

message User {
  string id = 1;
  string name = 2;
  string email = 3;
  int64 created_at = 4;
}

message GetUserRequest {
  string id = 1;
}
```

### When to Use gRPC

**Use gRPC for**:
- Internal service-to-service communication
- High-throughput, low-latency requirements
- Streaming data (real-time updates)
- Polyglot environments (auto-generates clients in many languages)

**Use REST for**:
- Public APIs (browser-friendly)
- Simple CRUD operations
- When human readability matters
- When you need broad client compatibility

---

## 8. API Gateway

An API gateway is a single entry point for all client requests.

```
                    ┌─────────────────────────────┐
Clients ───────────▶│         API Gateway          │
                    │                              │
                    │  • Authentication            │
                    │  • Rate limiting             │
                    │  • Request routing           │
                    │  • SSL termination           │
                    │  • Request/response transform│
                    │  • Logging & monitoring      │
                    └──────────────┬───────────────┘
                                   │
              ┌────────────────────┼────────────────────┐
              ▼                    ▼                    ▼
        ┌──────────┐        ┌──────────┐        ┌──────────┐
        │  User    │        │  Order   │        │  Payment │
        │ Service  │        │ Service  │        │ Service  │
        └──────────┘        └──────────┘        └──────────┘
```

**API Gateway responsibilities**:
- Authentication (verify JWT tokens)
- Authorization (check permissions)
- Rate limiting (per client)
- Request routing (to correct service)
- SSL termination
- Request/response transformation
- Logging and monitoring
- Circuit breaking

---

## References
- [REST API Design Best Practices](https://restfulapi.net/)
- [gRPC Documentation](https://grpc.io/docs/)
- [API Design Guide by Google](https://cloud.google.com/apis/design)
- [Stripe API Design](https://stripe.com/docs/api) — A gold standard for REST API design
