"""
Request Tracer — Day 2: Networking & Protocols

Traces an HTTP request and shows timing for each phase:
DNS lookup, TCP connection, TLS handshake, TTFB, download.

Usage: python request_tracer.py https://httpbin.org/get
"""

import sys
import time
import socket
import ssl
import urllib.parse
import http.client


def trace_request(url: str) -> dict:
    """
    Make an HTTP/HTTPS request and measure timing for each phase.
    Returns a dict with timing breakdown.
    """
    parsed = urllib.parse.urlparse(url)
    host = parsed.hostname
    path = parsed.path or "/"
    if parsed.query:
        path += "?" + parsed.query
    use_ssl = parsed.scheme == "https"
    port = parsed.port or (443 if use_ssl else 80)

    timings = {}

    # ─── Phase 1: DNS Resolution ──────────────────────────────────────────────
    t0 = time.perf_counter()
    try:
        ip = socket.gethostbyname(host)
    except socket.gaierror as e:
        print(f"DNS resolution failed: {e}")
        sys.exit(1)
    timings["dns_ms"] = round((time.perf_counter() - t0) * 1000, 2)

    # ─── Phase 2: TCP Connection ──────────────────────────────────────────────
    t1 = time.perf_counter()
    sock = socket.create_connection((ip, port), timeout=10)
    timings["tcp_ms"] = round((time.perf_counter() - t1) * 1000, 2)

    # ─── Phase 3: TLS Handshake (HTTPS only) ─────────────────────────────────
    if use_ssl:
        t2 = time.perf_counter()
        context = ssl.create_default_context()
        sock = context.wrap_socket(sock, server_hostname=host)
        timings["tls_ms"] = round((time.perf_counter() - t2) * 1000, 2)
    else:
        timings["tls_ms"] = 0

    # ─── Phase 4: Send Request ────────────────────────────────────────────────
    t3 = time.perf_counter()
    request = (
        f"GET {path} HTTP/1.1\r\n"
        f"Host: {host}\r\n"
        f"Connection: close\r\n"
        f"User-Agent: request-tracer/1.0\r\n"
        f"\r\n"
    )
    sock.sendall(request.encode())

    # ─── Phase 5: Time to First Byte ─────────────────────────────────────────
    first_byte = sock.recv(1)
    timings["ttfb_ms"] = round((time.perf_counter() - t3) * 1000, 2)

    # ─── Phase 6: Download Response ──────────────────────────────────────────
    t4 = time.perf_counter()
    response_data = first_byte
    while True:
        chunk = sock.recv(4096)
        if not chunk:
            break
        response_data += chunk
    timings["download_ms"] = round((time.perf_counter() - t4) * 1000, 2)

    sock.close()

    # Parse response
    response_text = response_data.decode("utf-8", errors="replace")
    status_line = response_text.split("\r\n")[0]
    status_code = int(status_line.split(" ")[1]) if " " in status_line else 0
    body_size = len(response_data.split(b"\r\n\r\n", 1)[-1])

    timings["total_ms"] = round(
        timings["dns_ms"] + timings["tcp_ms"] + timings["tls_ms"] +
        timings["ttfb_ms"] + timings["download_ms"], 2
    )
    timings["status_code"] = status_code
    timings["body_bytes"] = body_size
    timings["ip"] = ip

    return timings


def print_waterfall(url: str, timings: dict):
    """Print a visual waterfall chart of request timing."""
    total = timings["total_ms"]
    bar_width = 40

    def bar(ms):
        filled = int((ms / max(total, 1)) * bar_width)
        return "█" * filled + "░" * (bar_width - filled)

    print(f"\n{'='*60}")
    print(f"  Request Trace: {url}")
    print(f"{'='*60}")
    print(f"  Resolved IP:   {timings['ip']}")
    print(f"  Status Code:   {timings['status_code']}")
    print(f"  Body Size:     {timings['body_bytes']} bytes")
    print(f"{'─'*60}")
    print(f"  Phase              Time (ms)   Waterfall")
    print(f"{'─'*60}")
    print(f"  DNS Lookup         {timings['dns_ms']:>8.1f}ms  {bar(timings['dns_ms'])}")
    print(f"  TCP Connect        {timings['tcp_ms']:>8.1f}ms  {bar(timings['tcp_ms'])}")
    print(f"  TLS Handshake      {timings['tls_ms']:>8.1f}ms  {bar(timings['tls_ms'])}")
    print(f"  Time to 1st Byte   {timings['ttfb_ms']:>8.1f}ms  {bar(timings['ttfb_ms'])}")
    print(f"  Download           {timings['download_ms']:>8.1f}ms  {bar(timings['download_ms'])}")
    print(f"{'─'*60}")
    print(f"  TOTAL              {timings['total_ms']:>8.1f}ms")
    print(f"{'='*60}")

    # Analysis
    print("\n  💡 Analysis:")
    if timings["dns_ms"] > 50:
        print("  ⚠️  DNS lookup is slow. Consider DNS prefetching or a faster resolver.")
    if timings["tls_ms"] > 100:
        print("  ⚠️  TLS handshake is slow. Consider TLS session resumption.")
    if timings["ttfb_ms"] > 200:
        print("  ⚠️  TTFB is high. Server processing is slow. Consider caching.")
    if timings["download_ms"] > timings["ttfb_ms"] * 2:
        print("  ⚠️  Download time is high. Consider compression or a CDN.")

    dominant = max(
        [("DNS", timings["dns_ms"]), ("TCP", timings["tcp_ms"]),
         ("TLS", timings["tls_ms"]), ("TTFB", timings["ttfb_ms"]),
         ("Download", timings["download_ms"])],
        key=lambda x: x[1]
    )
    print(f"  📊 Dominant phase: {dominant[0]} ({dominant[1]}ms)")
    print()


def main():
    if len(sys.argv) < 2:
        url = "https://httpbin.org/get"
        print(f"No URL provided. Using default: {url}")
    else:
        url = sys.argv[1]

    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    print(f"\n🔍 Tracing request to: {url}")
    print("This shows you exactly where time is spent in a network request.\n")

    try:
        timings = trace_request(url)
        print_waterfall(url, timings)
    except Exception as e:
        print(f"Error: {e}")
        print("Try: python request_tracer.py https://httpbin.org/get")


if __name__ == "__main__":
    main()
