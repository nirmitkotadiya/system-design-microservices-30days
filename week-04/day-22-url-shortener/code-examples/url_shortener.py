"""
URL Shortener Implementation
============================
A production-ready URL shortener demonstrating:
- Base62 encoding for short codes
- Redis caching layer
- SQLite storage (swap for PostgreSQL in production)
- Click analytics
- Custom aliases
- Rate limiting

Run: python url_shortener.py
Requirements: pip install redis (optional - falls back to in-memory cache)
"""

import hashlib
import sqlite3
import time
import string
import random
from typing import Optional, Dict
from collections import defaultdict
from datetime import datetime


# ─────────────────────────────────────────────
# Base62 Encoding
# ─────────────────────────────────────────────

BASE62_CHARS = string.digits + string.ascii_letters  # 0-9, a-z, A-Z

def encode_base62(num: int) -> str:
    """Convert an integer to a base62 string."""
    if num == 0:
        return BASE62_CHARS[0]
    
    result = []
    while num > 0:
        result.append(BASE62_CHARS[num % 62])
        num //= 62
    
    return ''.join(reversed(result))

def decode_base62(s: str) -> int:
    """Convert a base62 string back to an integer."""
    result = 0
    for char in s:
        result = result * 62 + BASE62_CHARS.index(char)
    return result


# ─────────────────────────────────────────────
# Simple In-Memory Cache (Redis substitute)
# ─────────────────────────────────────────────

class SimpleCache:
    """
    In-memory LRU cache with TTL support.
    In production, replace with Redis.
    """
    
    def __init__(self, max_size: int = 10000, default_ttl: int = 3600):
        self._store: Dict[str, tuple] = {}  # key → (value, expires_at)
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.hits = 0
        self.misses = 0
    
    def get(self, key: str) -> Optional[str]:
        if key not in self._store:
            self.misses += 1
            return None
        
        value, expires_at = self._store[key]
        if expires_at and time.time() > expires_at:
            del self._store[key]
            self.misses += 1
            return None
        
        self.hits += 1
        return value
    
    def set(self, key: str, value: str, ttl: Optional[int] = None):
        if len(self._store) >= self.max_size:
            # Evict oldest entry (simplified LRU)
            oldest_key = next(iter(self._store))
            del self._store[oldest_key]
        
        expires_at = time.time() + (ttl or self.default_ttl) if ttl != -1 else None
        self._store[key] = (value, expires_at)
    
    def delete(self, key: str):
        self._store.pop(key, None)
    
    def hit_rate(self) -> float:
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0


# ─────────────────────────────────────────────
# Database Layer
# ─────────────────────────────────────────────

class URLDatabase:
    """
    SQLite-backed URL storage.
    In production: PostgreSQL with read replicas.
    """
    
    def __init__(self, db_path: str = ":memory:"):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._create_tables()
    
    def _create_tables(self):
        self.conn.executescript("""
            CREATE TABLE IF NOT EXISTS urls (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                short_code  TEXT UNIQUE NOT NULL,
                long_url    TEXT NOT NULL,
                user_id     TEXT,
                created_at  REAL NOT NULL,
                expires_at  REAL,
                is_active   INTEGER DEFAULT 1
            );
            
            CREATE INDEX IF NOT EXISTS idx_short_code ON urls(short_code);
            CREATE INDEX IF NOT EXISTS idx_long_url ON urls(long_url);
            
            CREATE TABLE IF NOT EXISTS clicks (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                short_code  TEXT NOT NULL,
                clicked_at  REAL NOT NULL,
                ip_address  TEXT,
                user_agent  TEXT,
                referrer    TEXT,
                country     TEXT
            );
            
            CREATE INDEX IF NOT EXISTS idx_clicks_code ON clicks(short_code);
            CREATE INDEX IF NOT EXISTS idx_clicks_time ON clicks(clicked_at);
        """)
        self.conn.commit()
    
    def save_url(self, short_code: str, long_url: str, 
                 user_id: Optional[str] = None,
                 expires_at: Optional[float] = None) -> int:
        cursor = self.conn.execute(
            """INSERT INTO urls (short_code, long_url, user_id, created_at, expires_at)
               VALUES (?, ?, ?, ?, ?)""",
            (short_code, long_url, user_id, time.time(), expires_at)
        )
        self.conn.commit()
        return cursor.lastrowid
    
    def get_url(self, short_code: str) -> Optional[Dict]:
        row = self.conn.execute(
            """SELECT short_code, long_url, created_at, expires_at, is_active
               FROM urls WHERE short_code = ?""",
            (short_code,)
        ).fetchone()
        
        if not row:
            return None
        
        return {
            "short_code": row[0],
            "long_url": row[1],
            "created_at": row[2],
            "expires_at": row[3],
            "is_active": bool(row[4])
        }
    
    def get_by_long_url(self, long_url: str) -> Optional[str]:
        """Check if URL already shortened (deduplication)."""
        row = self.conn.execute(
            "SELECT short_code FROM urls WHERE long_url = ? AND is_active = 1",
            (long_url,)
        ).fetchone()
        return row[0] if row else None
    
    def record_click(self, short_code: str, ip_address: str = None,
                     user_agent: str = None, referrer: str = None):
        self.conn.execute(
            """INSERT INTO clicks (short_code, clicked_at, ip_address, user_agent, referrer)
               VALUES (?, ?, ?, ?, ?)""",
            (short_code, time.time(), ip_address, user_agent, referrer)
        )
        self.conn.commit()
    
    def get_analytics(self, short_code: str) -> Dict:
        """Get click analytics for a short URL."""
        total = self.conn.execute(
            "SELECT COUNT(*) FROM clicks WHERE short_code = ?",
            (short_code,)
        ).fetchone()[0]
        
        # Clicks per day (last 7 days)
        seven_days_ago = time.time() - (7 * 86400)
        recent = self.conn.execute(
            """SELECT DATE(clicked_at, 'unixepoch') as day, COUNT(*) as count
               FROM clicks 
               WHERE short_code = ? AND clicked_at > ?
               GROUP BY day ORDER BY day DESC""",
            (short_code, seven_days_ago)
        ).fetchall()
        
        return {
            "total_clicks": total,
            "clicks_by_day": [{"date": r[0], "count": r[1]} for r in recent]
        }
    
    def short_code_exists(self, short_code: str) -> bool:
        row = self.conn.execute(
            "SELECT 1 FROM urls WHERE short_code = ?", (short_code,)
        ).fetchone()
        return row is not None


# ─────────────────────────────────────────────
# ID Generator (Snowflake-inspired)
# ─────────────────────────────────────────────

class IDGenerator:
    """
    Generates unique, time-sortable IDs.
    Simplified version of Twitter's Snowflake.
    
    In production: use a distributed counter or Snowflake service.
    """
    
    def __init__(self, machine_id: int = 1):
        self.machine_id = machine_id & 0x3FF  # 10 bits
        self.sequence = 0
        self.last_timestamp = -1
        self.epoch = 1700000000000  # Custom epoch (Nov 2023)
    
    def next_id(self) -> int:
        timestamp = int(time.time() * 1000) - self.epoch
        
        if timestamp == self.last_timestamp:
            self.sequence = (self.sequence + 1) & 0xFFF  # 12 bits
            if self.sequence == 0:
                # Sequence overflow — wait for next millisecond
                while timestamp <= self.last_timestamp:
                    timestamp = int(time.time() * 1000) - self.epoch
        else:
            self.sequence = 0
        
        self.last_timestamp = timestamp
        
        # 41 bits timestamp | 10 bits machine | 12 bits sequence
        return (timestamp << 22) | (self.machine_id << 12) | self.sequence


# ─────────────────────────────────────────────
# Rate Limiter
# ─────────────────────────────────────────────

class RateLimiter:
    """
    Simple in-memory rate limiter using sliding window.
    In production: use Redis with Lua scripts for atomicity.
    """
    
    def __init__(self, max_requests: int = 10, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._windows: Dict[str, list] = defaultdict(list)
    
    def is_allowed(self, identifier: str) -> bool:
        """Check if request is allowed. Returns True if allowed."""
        now = time.time()
        window_start = now - self.window_seconds
        
        # Remove old requests outside the window
        self._windows[identifier] = [
            ts for ts in self._windows[identifier] if ts > window_start
        ]
        
        if len(self._windows[identifier]) >= self.max_requests:
            return False
        
        self._windows[identifier].append(now)
        return True


# ─────────────────────────────────────────────
# URL Shortener Service
# ─────────────────────────────────────────────

class URLShortener:
    """
    Main URL shortener service.
    
    Architecture:
      - Cache (Redis/in-memory) for hot URLs
      - Database (PostgreSQL/SQLite) for persistence
      - ID generator for unique short codes
      - Rate limiter for abuse prevention
    """
    
    BASE_URL = "https://short.ly/"
    MIN_CODE_LENGTH = 6
    
    def __init__(self):
        self.db = URLDatabase()
        self.cache = SimpleCache(max_size=100000, default_ttl=3600)
        self.id_gen = IDGenerator(machine_id=1)
        self.rate_limiter = RateLimiter(max_requests=100, window_seconds=3600)
    
    def shorten(self, long_url: str, 
                custom_alias: Optional[str] = None,
                user_id: Optional[str] = None,
                ttl_days: Optional[int] = None) -> Dict:
        """
        Shorten a URL.
        
        Returns: {"short_url": "...", "short_code": "...", "long_url": "..."}
        """
        # Rate limiting
        identifier = user_id or "anonymous"
        if not self.rate_limiter.is_allowed(identifier):
            raise Exception("Rate limit exceeded. Try again later.")
        
        # Validate URL (basic check)
        if not long_url.startswith(("http://", "https://")):
            raise ValueError("URL must start with http:// or https://")
        
        # Check for existing short URL (deduplication)
        if not custom_alias:
            existing = self.db.get_by_long_url(long_url)
            if existing:
                return self._build_response(existing, long_url)
        
        # Generate or validate short code
        if custom_alias:
            short_code = self._validate_custom_alias(custom_alias)
        else:
            short_code = self._generate_short_code()
        
        # Calculate expiry
        expires_at = None
        if ttl_days:
            expires_at = time.time() + (ttl_days * 86400)
        
        # Save to database
        self.db.save_url(short_code, long_url, user_id, expires_at)
        
        # Cache it
        self.cache.set(short_code, long_url, ttl=ttl_days * 86400 if ttl_days else None)
        
        return self._build_response(short_code, long_url)
    
    def resolve(self, short_code: str, 
                ip_address: str = None,
                user_agent: str = None) -> Optional[str]:
        """
        Resolve a short code to the original URL.
        Records click analytics.
        
        Returns: long_url or None if not found/expired
        """
        # Check cache first (fast path)
        cached_url = self.cache.get(short_code)
        if cached_url:
            # Record click asynchronously (in production: use a queue)
            self.db.record_click(short_code, ip_address, user_agent)
            return cached_url
        
        # Cache miss — check database
        url_data = self.db.get_url(short_code)
        
        if not url_data:
            return None
        
        if not url_data["is_active"]:
            return None
        
        # Check expiry
        if url_data["expires_at"] and time.time() > url_data["expires_at"]:
            return None
        
        long_url = url_data["long_url"]
        
        # Populate cache
        self.cache.set(short_code, long_url)
        
        # Record click
        self.db.record_click(short_code, ip_address, user_agent)
        
        return long_url
    
    def get_analytics(self, short_code: str) -> Dict:
        """Get click analytics for a short URL."""
        url_data = self.db.get_url(short_code)
        if not url_data:
            raise ValueError(f"Short code '{short_code}' not found")
        
        analytics = self.db.get_analytics(short_code)
        return {
            "short_url": self.BASE_URL + short_code,
            "long_url": url_data["long_url"],
            "created_at": datetime.fromtimestamp(url_data["created_at"]).isoformat(),
            **analytics
        }
    
    def _generate_short_code(self) -> str:
        """Generate a unique short code using Snowflake ID + base62 encoding."""
        unique_id = self.id_gen.next_id()
        short_code = encode_base62(unique_id)
        
        # Ensure minimum length
        while len(short_code) < self.MIN_CODE_LENGTH:
            short_code = BASE62_CHARS[0] + short_code
        
        return short_code
    
    def _validate_custom_alias(self, alias: str) -> str:
        """Validate and return a custom alias."""
        if len(alias) < 3 or len(alias) > 20:
            raise ValueError("Custom alias must be 3-20 characters")
        
        allowed = set(string.ascii_letters + string.digits + "-_")
        if not all(c in allowed for c in alias):
            raise ValueError("Custom alias can only contain letters, numbers, - and _")
        
        if self.db.short_code_exists(alias):
            raise ValueError(f"Custom alias '{alias}' is already taken")
        
        return alias
    
    def _build_response(self, short_code: str, long_url: str) -> Dict:
        return {
            "short_url": self.BASE_URL + short_code,
            "short_code": short_code,
            "long_url": long_url
        }
    
    def cache_stats(self) -> Dict:
        return {
            "hit_rate": f"{self.cache.hit_rate() * 100:.1f}%",
            "hits": self.cache.hits,
            "misses": self.cache.misses,
            "cached_items": len(self.cache._store)
        }


# ─────────────────────────────────────────────
# Demo
# ─────────────────────────────────────────────

def demo():
    print("=" * 60)
    print("URL Shortener Demo")
    print("=" * 60)
    
    shortener = URLShortener()
    
    # Basic shortening
    print("\n--- Basic URL Shortening ---")
    result = shortener.shorten("https://www.example.com/very/long/path/to/some/article?utm_source=newsletter&utm_medium=email")
    print(f"Original: {result['long_url'][:60]}...")
    print(f"Short:    {result['short_url']}")
    print(f"Code:     {result['short_code']}")
    
    # Deduplication
    print("\n--- Deduplication (same URL) ---")
    result2 = shortener.shorten("https://www.example.com/very/long/path/to/some/article?utm_source=newsletter&utm_medium=email")
    print(f"Same short code returned: {result['short_code'] == result2['short_code']}")
    
    # Custom alias
    print("\n--- Custom Alias ---")
    result3 = shortener.shorten("https://github.com/username/awesome-project", custom_alias="my-project")
    print(f"Short: {result3['short_url']}")
    
    # Resolve
    print("\n--- Resolving Short URLs ---")
    long_url = shortener.resolve(result['short_code'], ip_address="192.168.1.1")
    print(f"Resolved: {long_url[:60]}...")
    
    # Simulate clicks for analytics
    for _ in range(5):
        shortener.resolve(result['short_code'], ip_address=f"10.0.0.{random.randint(1,255)}")
    
    # Analytics
    print("\n--- Analytics ---")
    analytics = shortener.get_analytics(result['short_code'])
    print(f"Short URL: {analytics['short_url']}")
    print(f"Total clicks: {analytics['total_clicks']}")
    print(f"Created: {analytics['created_at']}")
    
    # Cache stats
    print("\n--- Cache Stats ---")
    stats = shortener.cache_stats()
    for k, v in stats.items():
        print(f"  {k}: {v}")
    
    # Base62 encoding demo
    print("\n--- Base62 Encoding ---")
    for num in [1, 100, 1000, 1000000, 999999999]:
        encoded = encode_base62(num)
        decoded = decode_base62(encoded)
        print(f"  {num:12d} → '{encoded}' → {decoded}")
    
    print("\n" + "=" * 60)
    print("Demo complete!")


if __name__ == "__main__":
    demo()
