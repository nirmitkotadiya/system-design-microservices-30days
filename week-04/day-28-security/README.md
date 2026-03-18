# Day 28: Security in Distributed Systems

## "Security Is Not a Feature — It's a Foundation"

**Estimated Time**: 2 hours  
**Difficulty**: Advanced  
**Prerequisites**: Weeks 1–3 complete

---

## Learning Objectives
- Identify common attack vectors in distributed systems
- Implement mTLS for service-to-service authentication
- Design secrets management with HashiCorp Vault
- Apply the principle of least privilege
- Create a security checklist for microservices

---

## Quick Summary

Security in distributed systems is harder than in monoliths. More services = more attack surface. More network calls = more opportunities for interception. More secrets = more things to protect.

The core insight: **security is not something you add at the end. Design it in from the beginning.**

---

## Files in This Folder

| File | Description |
|------|-------------|
| `concepts.md` | Attack vectors, mTLS, secrets management, security patterns |
| `exercises.md` | Security audit and hardening exercises |
| `security-checklist.md` | Comprehensive security checklist for microservices |

---

## Success Criteria

You've mastered Day 28 when you can:
- [ ] Identify the top 5 security risks in a microservices architecture
- [ ] Explain mTLS and how it differs from TLS
- [ ] Design a secrets management strategy
- [ ] Apply the principle of least privilege to service permissions
- [ ] Complete the security checklist for a given system

---

## Interview Questions for This Day
- "How do you secure service-to-service communication?"
- "How do you manage secrets in a microservices architecture?"
- "What is mTLS and why would you use it?"
- "What are the OWASP Top 10 and how do they apply to APIs?"
