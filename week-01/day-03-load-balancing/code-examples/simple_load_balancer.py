"""
Simple Load Balancer — Day 3: Load Balancing

Demonstrates round-robin, least-connections, and weighted algorithms.
Simulates backend servers with health checks.

Run: python simple_load_balancer.py
"""

import random
import time
import threading
from dataclasses import dataclass, field
from typing import Optional
from collections import deque


@dataclass
class BackendServer:
    """Represents a backend server behind the load balancer."""
    name: str
    weight: int = 1
    healthy: bool = True
    active_connections: int = 0
    total_requests: int = 0
    total_latency_ms: float = 0.0
    base_latency_ms: float = 20.0
    _lock: threading.Lock = field(default_factory=threading.Lock, repr=False)

    def handle_request(self, request_id: int) -> dict:
        """Simulate handling a request. Returns response info."""
        if not self.healthy:
            raise ConnectionError(f"{self.name} is unhealthy")

        with self._lock:
            self.active_connections += 1
            self.total_requests += 1

        # Simulate variable latency
        latency = self.base_latency_ms + random.uniform(0, 10)
        time.sleep(latency / 1000.0)

        with self._lock:
            self.active_connections -= 1
            self.total_latency_ms += latency

        return {
            "server": self.name,
            "request_id": request_id,
            "latency_ms": round(latency, 1),
        }

    @property
    def avg_latency_ms(self) -> float:
        if self.total_requests == 0:
            return 0.0
        return round(self.total_latency_ms / self.total_requests, 1)


class LoadBalancer:
    """
    Load balancer supporting multiple algorithms.
    """

    ALGORITHMS = ["round_robin", "least_connections", "weighted_round_robin", "random"]

    def __init__(self, servers: list[BackendServer], algorithm: str = "round_robin"):
        self.servers = servers
        self.algorithm = algorithm
        self._rr_index = 0
        self._lock = threading.Lock()
        self._request_count = 0

    def _healthy_servers(self) -> list[BackendServer]:
        return [s for s in self.servers if s.healthy]

    def get_server(self) -> Optional[BackendServer]:
        """Select a server based on the configured algorithm."""
        healthy = self._healthy_servers()
        if not healthy:
            return None

        with self._lock:
            if self.algorithm == "round_robin":
                server = healthy[self._rr_index % len(healthy)]
                self._rr_index += 1
                return server

            elif self.algorithm == "least_connections":
                return min(healthy, key=lambda s: s.active_connections)

            elif self.algorithm == "weighted_round_robin":
                # Build weighted pool
                pool = []
                for s in healthy:
                    pool.extend([s] * s.weight)
                server = pool[self._rr_index % len(pool)]
                self._rr_index += 1
                return server

            elif self.algorithm == "random":
                return random.choice(healthy)

        return healthy[0]

    def handle_request(self, request_id: int) -> dict:
        """Route a request to a backend server."""
        server = self.get_server()
        if server is None:
            return {"error": "No healthy servers available", "request_id": request_id}

        try:
            return server.handle_request(request_id)
        except ConnectionError as e:
            return {"error": str(e), "request_id": request_id}

    def print_stats(self):
        """Print current server statistics."""
        print(f"\n{'─'*55}")
        print(f"  {'Server':<12} {'Healthy':<8} {'Requests':<10} {'Active':<8} {'Avg Lat'}")
        print(f"{'─'*55}")
        for s in self.servers:
            status = "✓" if s.healthy else "✗"
            print(f"  {s.name:<12} {status:<8} {s.total_requests:<10} {s.active_connections:<8} {s.avg_latency_ms}ms")
        print(f"{'─'*55}")


def run_experiment(lb: LoadBalancer, num_requests: int, concurrent: int = 5):
    """Send requests to the load balancer and collect results."""
    results = []
    threads = []
    request_counter = [0]
    lock = threading.Lock()

    def send_request():
        with lock:
            request_counter[0] += 1
            req_id = request_counter[0]
        result = lb.handle_request(req_id)
        results.append(result)

    # Send requests in batches
    for batch_start in range(0, num_requests, concurrent):
        batch = []
        for _ in range(min(concurrent, num_requests - batch_start)):
            t = threading.Thread(target=send_request)
            t.start()
            batch.append(t)
        for t in batch:
            t.join()

    return results


def main():
    print("\n⚖️  LOAD BALANCER DEMO — Day 3: Load Balancing")
    print("=" * 60)

    # ─── Setup Servers ────────────────────────────────────────────
    servers = [
        BackendServer("server-1", weight=3, base_latency_ms=15),
        BackendServer("server-2", weight=2, base_latency_ms=20),
        BackendServer("server-3", weight=1, base_latency_ms=25),
    ]

    # ─── Experiment 1: Round Robin ────────────────────────────────
    print("\n📊 EXPERIMENT 1: Round Robin (30 requests)")
    for s in servers:
        s.total_requests = 0
        s.total_latency_ms = 0.0

    lb = LoadBalancer(servers, algorithm="round_robin")
    run_experiment(lb, num_requests=30, concurrent=3)
    lb.print_stats()
    print("  → Round robin distributes evenly regardless of server speed")

    # ─── Experiment 2: Weighted Round Robin ──────────────────────
    print("\n📊 EXPERIMENT 2: Weighted Round Robin (30 requests)")
    print("  Weights: server-1=3, server-2=2, server-3=1")
    for s in servers:
        s.total_requests = 0
        s.total_latency_ms = 0.0

    lb = LoadBalancer(servers, algorithm="weighted_round_robin")
    run_experiment(lb, num_requests=30, concurrent=3)
    lb.print_stats()
    print("  → Weighted RR sends more traffic to faster/more powerful servers")

    # ─── Experiment 3: Server Failure ────────────────────────────
    print("\n📊 EXPERIMENT 3: Server Failure (server-2 goes down)")
    for s in servers:
        s.total_requests = 0
        s.total_latency_ms = 0.0

    servers[1].healthy = False  # Take server-2 offline
    lb = LoadBalancer(servers, algorithm="round_robin")
    run_experiment(lb, num_requests=20, concurrent=3)
    lb.print_stats()
    print("  → Load balancer automatically routes around the failed server")

    # Bring server-2 back
    servers[1].healthy = True

    # ─── Experiment 4: Least Connections ─────────────────────────
    print("\n📊 EXPERIMENT 4: Least Connections (30 requests, mixed latency)")
    # Make server-3 much slower to simulate a loaded server
    servers[2].base_latency_ms = 200
    for s in servers:
        s.total_requests = 0
        s.total_latency_ms = 0.0

    lb = LoadBalancer(servers, algorithm="least_connections")
    run_experiment(lb, num_requests=30, concurrent=10)
    lb.print_stats()
    print("  → Least connections avoids the slow server naturally")

    print("\n💡 KEY TAKEAWAYS:")
    print("  1. Round robin is simple but ignores server capacity")
    print("  2. Weighted RR is better when servers have different specs")
    print("  3. Health checks ensure failed servers are bypassed automatically")
    print("  4. Least connections is best when request duration varies significantly")
    print()


if __name__ == "__main__":
    main()
