# Day 16: Exercises — API Design

---

## Exercise 1: Basic Comprehension (15 minutes)

1. What's the difference between PUT and PATCH? Give an example of when you'd use each.

2. A colleague designs this endpoint: `POST /deleteUser?id=123`. What's wrong with it? How would you fix it?

3. What's the difference between offset pagination and cursor pagination? When would you use each?

4. You're adding a new field `middle_name` to the user response. Is this a breaking change? What about removing the `phone_number` field?

5. When would you choose gRPC over REST for service-to-service communication?

---

## Exercise 2: Design a Twitter-like API (30 minutes)

Design the REST API for a Twitter-like service. Include:

**Resources**: Users, Tweets, Follows, Likes, Retweets

For each endpoint, specify:
- HTTP method
- URL
- Request body (if applicable)
- Response body
- Status codes

**Required endpoints**:
1. Create a tweet
2. Get a tweet by ID
3. Delete a tweet
4. Get a user's timeline (tweets from followed users)
5. Follow a user
6. Unfollow a user
7. Like a tweet
8. Unlike a tweet
9. Search tweets
10. Get trending topics

**Bonus**: Design the pagination for the timeline endpoint.

---

## Exercise 3: API Versioning Strategy (20 minutes)

### Scenario

You have a public API with 10,000 active clients. You need to make these changes:

**Change 1**: Add a new optional field `bio` to the user response  
**Change 2**: Rename `username` to `handle` in the user response  
**Change 3**: Change the `created_at` field from Unix timestamp to ISO 8601 string  
**Change 4**: Remove the deprecated `phone_number` field  
**Change 5**: Add a new endpoint `GET /users/{id}/followers`

For each change:
1. Is it breaking or non-breaking?
2. Does it require a new API version?
3. How do you communicate the change to clients?
4. What's the migration timeline?

---

## Exercise 4: Error Handling Design (20 minutes)

Design a consistent error response format for an API. Your format should:
- Be consistent across all endpoints
- Include enough information for clients to handle errors programmatically
- Include enough information for developers to debug
- Not expose sensitive information (stack traces, internal IDs)

**Scenarios to handle**:
1. Invalid request body (missing required field)
2. Resource not found
3. Unauthorized (not authenticated)
4. Forbidden (authenticated but not authorized)
5. Rate limited
6. Internal server error
7. Service unavailable (downstream service down)

For each, specify: HTTP status code, error code, message, and any additional fields.

---

## Exercise 5: Challenge — Design a Complete API for a Ride-Sharing App (35 minutes)

Design the complete REST API for a ride-sharing app (like Uber):

**Core flows**:
1. Rider requests a ride
2. Driver accepts a ride
3. Driver updates location during ride
4. Ride completes, payment processed
5. Both parties rate each other

**Design requirements**:
1. **Authentication**: How do you authenticate riders vs. drivers?
2. **Real-time updates**: How does the rider see the driver's location in real-time? (REST polling? WebSocket? SSE?)
3. **Idempotency**: If a rider accidentally taps "Request Ride" twice, how do you prevent two rides from being created?
4. **Versioning**: You need to support both v1 (old app) and v2 (new app) simultaneously. How?
5. **Rate limiting**: What rate limits do you apply to which endpoints?

---

## Hints

**Exercise 2**: For the timeline, cursor pagination is better than offset (new tweets are constantly being added).

**Exercise 4**: Never return stack traces in production. Use error codes that clients can handle programmatically (e.g., `INSUFFICIENT_FUNDS` is more useful than `Internal Server Error`).

**Exercise 5, Idempotency**: Use an idempotency key in the request header. If the same key is used twice, return the same response.

---

## Self-Assessment Checklist

- [ ] I can design a RESTful API following best practices
- [ ] I understand the difference between PUT and PATCH
- [ ] I can design cursor-based pagination
- [ ] I know the difference between breaking and non-breaking API changes
- [ ] I can design a consistent error response format
- [ ] I understand when to use gRPC vs. REST
