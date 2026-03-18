# Day 28: Exercises — Security in Distributed Systems

---

## Exercise 1: Threat Modeling (20 minutes)

For a payment processing microservice, identify:

1. **Assets**: What are you protecting? (List at least 5)

2. **Threats**: For each asset, what are the top 2 threats?

3. **Attack vectors**: How could an attacker reach each asset?

4. **Mitigations**: For each threat, what control prevents it?

Use this table:

| Asset | Threat | Attack Vector | Mitigation |
|-------|--------|---------------|------------|
| Credit card numbers | Theft | SQL injection | Parameterized queries + encryption |
| ? | ? | ? | ? |

---

## Exercise 2: Security Code Review (25 minutes)

Find and fix the security vulnerabilities in this code:

```python
import os
import sqlite3
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# Database connection
DB_PASSWORD = "admin123"  # Vulnerability 1
conn = sqlite3.connect("users.db")

@app.route("/api/users/<user_id>")
def get_user(user_id):
    # Vulnerability 2
    query = f"SELECT * FROM users WHERE id = {user_id}"
    result = conn.execute(query).fetchone()
    return jsonify(result)

@app.route("/api/fetch")
def fetch_url():
    url = request.args.get("url")
    # Vulnerability 3
    response = requests.get(url)
    return response.text

@app.route("/api/login", methods=["POST"])
def login():
    data = request.json
    # Vulnerability 4
    query = f"SELECT * FROM users WHERE email = '{data['email']}' AND password = '{data['password']}'"
    user = conn.execute(query).fetchone()
    if user:
        # Vulnerability 5
        token = f"user_{user['id']}_authenticated"
        return jsonify({"token": token})
    return jsonify({"error": "Invalid credentials"}), 401

@app.route("/api/admin/users")
def list_all_users():
    # Vulnerability 6
    return jsonify(conn.execute("SELECT * FROM users").fetchall())
```

For each vulnerability:
1. What is the vulnerability?
2. What attack does it enable?
3. How do you fix it?

---

## Exercise 3: mTLS Design (20 minutes)

### Scenario

You have 5 microservices:
- API Gateway (public-facing)
- Order Service
- Payment Service
- Inventory Service
- User Service

**Design the mTLS configuration**:

1. Which services should communicate with which? (Draw the allowed communication matrix)

2. How do you issue and rotate certificates? (Manual? Automated with cert-manager?)

3. What happens when a certificate expires? How do you prevent service outages?

4. How do you handle a compromised service? (Revoke its certificate)

5. How do you test that mTLS is working? (What would you check?)

---

## Exercise 4: Secrets Management Design (20 minutes)

### Scenario

Your microservices need these secrets:
- Database passwords (one per service)
- API keys for third-party services (Stripe, SendGrid, Twilio)
- JWT signing keys
- Encryption keys for PII data

**Design the secrets management strategy**:

1. Where do secrets live? (Vault, AWS Secrets Manager, Kubernetes Secrets?)

2. How do services authenticate to the secrets manager?

3. How often are secrets rotated? Who triggers rotation?

4. What happens if the secrets manager is unavailable? (Fallback strategy)

5. How do you audit secret access? (Who accessed what, when?)

---

## Exercise 5: Challenge — Security Audit (35 minutes)

### Scenario

Perform a security audit of the Twitter design from Day 24.

**Audit areas**:

1. **Authentication**: How are users authenticated? How are services authenticated to each other?

2. **Authorization**: Can User A access User B's DMs? How is this prevented?

3. **Data protection**: Where is user data stored? Is it encrypted? What PII is collected?

4. **API security**: What rate limiting is in place? What input validation?

5. **Secrets**: Where are database passwords stored? How are they rotated?

6. **Monitoring**: What security events are logged? What triggers an alert?

For each area, identify:
- Current state (from the Day 24 design)
- Vulnerabilities
- Recommended improvements

---

## Hints

**Exercise 2**: 
- Vulnerability 1: Hardcoded password
- Vulnerability 2: SQL injection
- Vulnerability 3: SSRF
- Vulnerability 4: SQL injection + plaintext password comparison
- Vulnerability 5: Predictable/forgeable token
- Vulnerability 6: Missing authentication

**Exercise 3**: Use a service mesh (Istio) to automate certificate management. cert-manager handles certificate rotation automatically.

---

## Self-Assessment Checklist

- [ ] I can identify common security vulnerabilities in code
- [ ] I understand mTLS and how it differs from TLS
- [ ] I can design a secrets management strategy
- [ ] I can perform a basic security audit of a system design
- [ ] I know the OWASP API Security Top 10
- [ ] I understand defense in depth
