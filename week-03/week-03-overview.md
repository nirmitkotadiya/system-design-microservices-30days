# Week 3: Microservices & Modern Architecture

## Focus Area
Breaking the monolith. This week covers how large engineering organizations structure their systems — and the very real pain points that come with microservices that nobody warns you about.

## Prerequisites
- Weeks 1 and 2 complete
- Understanding of REST APIs
- Basic familiarity with Docker

## Learning Objectives
By the end of Week 3, you will be able to:
- Decompose a monolith into microservices using domain-driven design principles
- Design REST and gRPC APIs with proper versioning
- Explain service discovery and implement a basic service mesh
- Handle distributed transactions using Saga and 2PC patterns
- Set up observability (metrics, logs, traces) for a distributed system
- Explain CDN architecture and edge computing patterns

## Day-by-Day Breakdown

| Day | Topic | Key Concept | Deliverable |
|-----|-------|-------------|-------------|
| 15 | Microservices Architecture | Decomposition, bounded contexts | Decompose an e-commerce monolith |
| 16 | API Design & REST/gRPC | REST principles, gRPC, versioning | Design a complete API |
| 17 | Service Discovery & Mesh | Consul, Istio, sidecar pattern | Design service mesh topology |
| 18 | Distributed Transactions | Saga, 2PC, eventual consistency | Handle a payment transaction |
| 19 | Observability & Monitoring | Metrics, logs, traces (the three pillars) | Design observability stack |
| 20 | CDN & Edge Computing | Edge caching, edge functions | Design CDN strategy |
| 21 | Week 3 Review | Synthesis | Design a ride-sharing backend |

## Required Tools
- Docker Compose (for multi-service examples)
- Prometheus + Grafana (via Docker)
- Python with `grpcio` library
- Jaeger (distributed tracing)

## Success Criteria
You've mastered Week 3 when you can:
- [ ] Explain the difference between a microservice and a monolith
- [ ] Describe the Saga pattern and when to use it vs. 2PC
- [ ] Explain what a service mesh does and why you'd want one
- [ ] Describe the three pillars of observability
- [ ] Design an API with proper versioning strategy
- [ ] Explain how a CDN reduces latency

## Resources for This Week
- DDIA Chapter 12 (The Future of Data Systems)
- [Building Microservices by Sam Newman](https://samnewman.io/books/building_microservices/)
- [Istio Documentation](https://istio.io/latest/docs/)
- [OpenTelemetry Documentation](https://opentelemetry.io/docs/)
- [Martin Fowler on Microservices](https://martinfowler.com/articles/microservices.html)

## Progress Checklist
- [ ] Day 15: Microservices decomposition understood
- [ ] Day 16: API design principles applied
- [ ] Day 17: Service discovery patterns understood
- [ ] Day 18: Distributed transaction patterns understood
- [ ] Day 19: Observability stack designed
- [ ] Day 20: CDN strategy understood
- [ ] Day 21: Review complete and ride-sharing backend designed
