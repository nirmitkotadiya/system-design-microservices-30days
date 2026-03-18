# Security Checklist for Microservices

Use this checklist when reviewing any microservices architecture.

---

## Authentication & Authorization

- [ ] All external APIs require authentication (JWT, API key, OAuth)
- [ ] JWT tokens have short expiry (15-60 minutes)
- [ ] Refresh tokens are rotated on use
- [ ] Service-to-service calls use mTLS
- [ ] Authorization checks are performed at the service level (not just API gateway)
- [ ] Principle of least privilege: services only have permissions they need
- [ ] Admin endpoints are protected with additional authentication
- [ ] Failed authentication attempts are rate limited and logged

---

## Secrets Management

- [ ] No secrets in source code or version control
- [ ] No secrets in environment variables (use secrets manager)
- [ ] Secrets are rotated regularly (or dynamically generated)
- [ ] Secrets access is audited
- [ ] Database credentials are service-specific (not shared)
- [ ] API keys are scoped to minimum required permissions
- [ ] Encryption keys are managed separately from data

---

## Network Security

- [ ] All traffic encrypted in transit (TLS 1.2+)
- [ ] Internal services not exposed to public internet
- [ ] Network segmentation (services can only talk to services they need to)
- [ ] Firewall rules follow principle of least privilege
- [ ] DDoS protection at the edge (CDN, WAF)
- [ ] Rate limiting on all public endpoints

---

## Input Validation

- [ ] All user input is validated and sanitized
- [ ] SQL queries use parameterized statements (no string concatenation)
- [ ] File uploads are validated (type, size, content)
- [ ] URL parameters are validated
- [ ] JSON/XML parsing is safe (no XXE, no billion laughs)
- [ ] SSRF protection: validate URLs before fetching

---

## Data Protection

- [ ] Sensitive data encrypted at rest (database encryption)
- [ ] PII is identified and handled according to regulations (GDPR, CCPA)
- [ ] Passwords are hashed with bcrypt/argon2 (not MD5/SHA1)
- [ ] Credit card data is not stored (use tokenization)
- [ ] Data retention policies are defined and enforced
- [ ] Backups are encrypted

---

## Logging & Monitoring

- [ ] All authentication events are logged
- [ ] All authorization failures are logged
- [ ] Logs do not contain sensitive data (passwords, tokens, PII)
- [ ] Anomaly detection alerts on unusual patterns
- [ ] Security events trigger alerts (multiple failed logins, unusual data access)
- [ ] Audit trail for sensitive operations (data deletion, admin actions)

---

## Dependency Security

- [ ] Dependencies are regularly updated
- [ ] Known vulnerabilities are tracked (Snyk, Dependabot)
- [ ] Container images are scanned for vulnerabilities
- [ ] Base images are minimal (distroless, alpine)
- [ ] Supply chain security (verify package signatures)

---

## Incident Response

- [ ] Security incident response plan exists
- [ ] On-call rotation includes security incidents
- [ ] Runbooks for common security incidents
- [ ] Ability to revoke compromised credentials quickly
- [ ] Ability to block compromised users/services quickly
- [ ] Post-incident review process

---

## Compliance

- [ ] GDPR: Right to deletion implemented
- [ ] GDPR: Data portability implemented
- [ ] PCI DSS: If handling payments, compliance verified
- [ ] SOC 2: If required by customers, controls in place
- [ ] Regular security audits and penetration testing
