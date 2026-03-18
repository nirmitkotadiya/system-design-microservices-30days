# Day 28: Security in Distributed Systems — Concepts Deep Dive

## 1. The Threat Model

Before securing a system, understand what you're protecting against:

```
Threats:
  External attackers: Trying to access data they shouldn't
  Compromised services: One service is hacked, can it access others?
  Insider threats: Malicious employees
  Supply chain attacks: Compromised dependencies
  Data breaches: Unauthorized data access/exfiltration

Assets to protect:
  User data (PII, passwords, payment info)
  Business data (trade secrets, financial data)
  Infrastructure (servers, databases, secrets)
  Service availability (DDoS protection)
```

---

## 2. Authentication vs. Authorization

**Authentication**: Who are you?  
**Authorization**: What are you allowed to do?

```
Authentication: "I am user_123, here's my JWT token"
Authorization: "User_123 is allowed to read their own orders but not others'"
```

### JWT (JSON Web Tokens)

```
Header.Payload.Signature

Header: {"alg": "RS256", "typ": "JWT"}
Payload: {
  "sub": "user_123",
  "email": "alice@example.com",
  "roles": ["user"],
  "exp": 1700000000,
  "iat": 1699996400
}
Signature: HMACSHA256(base64(header) + "." + base64(payload), secret)
```

**Verify**: Check signature, check expiry, check issuer  
**Never**: Store sensitive data in JWT payload (it's base64 encoded, not encrypted)

---

## 3. mTLS (Mutual TLS)

Regular TLS: Client verifies server's identity.  
mTLS: Both client AND server verify each other's identity.

```
Regular TLS:
  Client → "Are you really api.example.com?" → Server presents certificate
  Client verifies certificate → Encrypted channel established

mTLS:
  Client → "Are you really payment-service?" → Server presents certificate
  Server → "Are you really order-service?" → Client presents certificate
  Both verify → Encrypted channel established
```

### Why mTLS for Microservices?

```
Without mTLS:
  Attacker compromises one service
  Attacker can call any other service (no authentication)
  
With mTLS:
  Each service has a certificate
  Services only accept connections from services with valid certificates
  Compromised service can only call services it's authorized to call
```

### Implementing mTLS with a Service Mesh

```yaml
# Istio: Enable mTLS for all services in namespace
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: default
  namespace: production
spec:
  mtls:
    mode: STRICT  # Reject non-mTLS connections
```

---

## 4. Secrets Management

### The Problem with Hardcoded Secrets

```python
# BAD: Secret in code
DB_PASSWORD = "super_secret_password_123"

# BAD: Secret in environment variable (still visible in process list)
DB_PASSWORD = os.environ["DB_PASSWORD"]

# GOOD: Fetch from secrets manager at runtime
DB_PASSWORD = vault.get_secret("database/production/password")
```

### HashiCorp Vault

Vault is a secrets management tool that:
- Stores secrets encrypted at rest
- Controls access with fine-grained policies
- Rotates secrets automatically
- Audits all secret access

```python
import hvac

client = hvac.Client(url='https://vault.example.com')
client.auth.kubernetes.login(role='order-service', jwt=k8s_jwt)

# Read a secret
secret = client.secrets.kv.v2.read_secret_version(
    path='database/production',
    mount_point='secret'
)
db_password = secret['data']['data']['password']
```

### Dynamic Secrets

Vault can generate short-lived credentials on demand:

```
Order Service → Vault: "I need database credentials"
Vault → Creates temporary PostgreSQL user with limited permissions
Vault → Returns: {username: "order-svc-abc123", password: "...", ttl: "1h"}
Order Service → Connects to DB with temporary credentials
After 1 hour → Credentials automatically revoked
```

**Benefits**: No long-lived credentials, automatic rotation, audit trail

---

## 5. API Security

### Input Validation

```python
from pydantic import BaseModel, validator, constr

class CreateOrderRequest(BaseModel):
    user_id: str
    items: list[OrderItem]
    shipping_address: str

    @validator('user_id')
    def validate_user_id(cls, v):
        if not v.startswith('user_'):
            raise ValueError('Invalid user_id format')
        return v

    @validator('items')
    def validate_items(cls, v):
        if len(v) == 0:
            raise ValueError('Order must have at least one item')
        if len(v) > 100:
            raise ValueError('Order cannot have more than 100 items')
        return v
```

### SQL Injection Prevention

```python
# BAD: String concatenation
query = f"SELECT * FROM users WHERE email = '{email}'"

# GOOD: Parameterized queries
query = "SELECT * FROM users WHERE email = ?"
cursor.execute(query, (email,))
```

### OWASP API Security Top 10

1. **Broken Object Level Authorization**: User A can access User B's data
2. **Broken Authentication**: Weak tokens, no rate limiting on login
3. **Broken Object Property Level Authorization**: User can modify fields they shouldn't
4. **Unrestricted Resource Consumption**: No rate limiting, no pagination limits
5. **Broken Function Level Authorization**: Regular user can call admin endpoints
6. **Unrestricted Access to Sensitive Business Flows**: Automated abuse of business logic
7. **Server Side Request Forgery (SSRF)**: Server fetches attacker-controlled URLs
8. **Security Misconfiguration**: Default credentials, verbose error messages
9. **Improper Inventory Management**: Undocumented/deprecated APIs still accessible
10. **Unsafe Consumption of APIs**: Trusting third-party API responses without validation

---

## 6. Defense in Depth

Don't rely on a single security control. Layer multiple defenses:

```
Layer 1: Network (firewall, VPC, security groups)
  → Only allow traffic from known sources

Layer 2: Transport (TLS, mTLS)
  → Encrypt all traffic, authenticate services

Layer 3: Application (authentication, authorization)
  → Verify identity, check permissions

Layer 4: Data (encryption at rest, field-level encryption)
  → Encrypt sensitive data in the database

Layer 5: Monitoring (audit logs, anomaly detection)
  → Detect and respond to breaches
```

---

## 7. Common Attack Scenarios

### Scenario 1: Compromised Service
```
Attacker compromises Order Service
Without mTLS: Attacker can call Payment Service directly
With mTLS: Payment Service rejects connections without valid certificate
```

### Scenario 2: Stolen JWT Token
```
Attacker steals user's JWT token
Without short expiry: Token valid for days/weeks
With short expiry (15 min) + refresh tokens: Token expires quickly
```

### Scenario 3: SQL Injection
```
Attacker sends: email = "'; DROP TABLE users; --"
Without parameterized queries: Database executes DROP TABLE
With parameterized queries: Input is treated as data, not SQL
```

### Scenario 4: SSRF (Server-Side Request Forgery)
```
API endpoint: POST /api/fetch-url {"url": "https://..."}
Attacker sends: {"url": "http://169.254.169.254/latest/meta-data/"}
Without validation: Server fetches AWS metadata (credentials!)
With validation: Reject internal IP addresses
```

---

## References
- [OWASP API Security Top 10](https://owasp.org/www-project-api-security/)
- [HashiCorp Vault Documentation](https://www.vaultproject.io/docs)
- [Istio Security Documentation](https://istio.io/latest/docs/concepts/security/)
- [Google BeyondCorp (Zero Trust)](https://cloud.google.com/beyondcorp)
