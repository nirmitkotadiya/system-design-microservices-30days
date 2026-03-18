"""
Load Simulator — Day 1: Scalability Fundamentals

Simulates a server under increasing load to demonstrate how
response time degrades as requests per second increases.

Run: python load_simulator.py
"""

import time
import random
import statistics
import threading
from collections import defaultdict


class Server:
    """
    Simulates a single server with a fixed capacity.
    When overloaded, requests queue up and latency increases.
    """

    def __init__(self, name: str, max_concurrent: int = 10, base_latency_ms: float = 20.0):
        self.name = name
        self.max_concurrent = max_concurrent
        self.base_latency_ms = base_latency_ms
        self._active_requests = 0
        self._lock = threading.Lock()

    def handle_request(self) -> float:
        """
        Process a request and return the latency in milliseconds.
        Latency increases as the server gets more loaded.
        """
        with self._lock:
            self._active_requests += 1
            load_factor = self._active_requests / self.max_concurrent

        # Simulate latency: increases non-linearly under load
        # This models real server behavior (queuing theory)
        if load_factor <= 0.5:
            latency = self.base_latency_ms * (1 + load_factor * 0.5)
        elif load_factor <= 0.8:
            latency = self.base_latency_ms * (1 + load_factor * 2)
        else:
            # Overloaded: latency spikes dramatically
            latency = self.base_latency_ms * (1 + load_factor * 10)

        # Add some random jitter (real servers aren't perfectly consistent)
        latency += random.uniform(0, latency * 0.2)

        # Simulate actual processing time
        time.sleep(latency / 1000.0)

        with self._lock:
            self._active_requests -= 1

        return latency


class LoadBalancer:
    """
    Simple round-robin load balancer across multiple servers.
    """

    def __init__(self, servers: list):
        self.servers = servers
        self._current = 0
        self._lock = threading.Lock()

    def get_server(self) -> Server:
        with self._lock:
            server = self.servers[self._current % len(self.servers)]
            self._current += 1
            return server

    def handle_request(self) -> float:
        server = self.get_server()
        return server.handle_request()


def run_load_test(handler, rps: int, duration_seconds: int = 3) -> dict:
    """
    Send requests at a given RPS and collect latency statistics.

    Args:
        handler: Server or LoadBalancer to send requests to
        rps: Requests per second to simulate
        duration_seconds: How long to run the test

    Returns:
        Dictionary with latency statistics
    """
    latencies = []
    errors = 0
    interval = 1.0 / rps
    threads = []

    def send_request():
        nonlocal errors
        try:
            latency = handler.handle_request()
            latencies.append(latency)
        except Exception:
            errors += 1

    start_time = time.time()
    while time.time() - start_time < duration_seconds:
        t = threading.Thread(target=send_request)
        t.start()
        threads.append(t)
        time.sleep(interval)

    # Wait for all requests to complete
    for t in threads:
        t.join(timeout=10)

    if not latencies:
        return {"error": "No successful requests"}

    latencies.sort()
    n = len(latencies)

    return {
        "rps": rps,
        "total_requests": n,
        "errors": errors,
        "p50_ms": round(latencies[int(n * 0.50)], 1),
        "p95_ms": round(latencies[int(n * 0.95)], 1),
        "p99_ms": round(latencies[int(n * 0.99)], 1),
        "avg_ms": round(statistics.mean(latencies), 1),
        "max_ms": round(max(latencies), 1),
    }


def print_results(results: dict, label: str):
    print(f"\n{'='*50}")
    print(f"  {label}")
    print(f"{'='*50}")
    print(f"  RPS:            {results['rps']}")
    print(f"  Total Requests: {results['total_requests']}")
    print(f"  Errors:         {results['errors']}")
    print(f"  Average:        {results['avg_ms']}ms")
    print(f"  p50 (median):   {results['p50_ms']}ms")
    print(f"  p95:            {results['p95_ms']}ms")
    print(f"  p99:            {results['p99_ms']}ms")
    print(f"  Max:            {results['max_ms']}ms")


def main():
    print("\n🔬 LOAD SIMULATOR — Day 1: Scalability Fundamentals")
    print("=" * 60)
    print("Simulating a server under increasing load...")
    print("Watch how p99 latency degrades as RPS increases.\n")

    # ─── EXPERIMENT 1: Single Server Under Increasing Load ───────────────────
    print("\n📊 EXPERIMENT 1: Single Server Under Increasing Load")
    print("Server capacity: 10 concurrent requests, 20ms base latency")

    single_server = Server(name="server-1", max_concurrent=10, base_latency_ms=20.0)

    for rps in [5, 10, 20, 40]:
        results = run_load_test(single_server, rps=rps, duration_seconds=2)
        print_results(results, f"Single Server @ {rps} RPS")

    # ─── EXPERIMENT 2: Load Balanced Across 3 Servers ────────────────────────
    print("\n\n📊 EXPERIMENT 2: Load Balanced Across 3 Servers")
    print("Same total capacity, but distributed across 3 servers")

    servers = [
        Server(name=f"server-{i}", max_concurrent=10, base_latency_ms=20.0)
        for i in range(1, 4)
    ]
    lb = LoadBalancer(servers)

    for rps in [5, 10, 20, 40]:
        results = run_load_test(lb, rps=rps, duration_seconds=2)
        print_results(results, f"3-Server LB @ {rps} RPS")

    # ─── KEY OBSERVATIONS ────────────────────────────────────────────────────
    print("\n\n💡 KEY OBSERVATIONS:")
    print("1. p99 latency spikes dramatically before p50 does")
    print("   → Average latency hides the worst user experiences")
    print("2. The load balancer distributes load, delaying the spike")
    print("   → Horizontal scaling buys you headroom")
    print("3. Even with 3 servers, there's still a limit")
    print("   → You need to keep adding capacity as load grows")
    print("\nThis is why we measure p99, not average latency.")
    print("And why horizontal scaling is a core pattern.\n")


if __name__ == "__main__":
    main()
