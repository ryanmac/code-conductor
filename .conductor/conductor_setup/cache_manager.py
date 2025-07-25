"""High-performance cache for all setup operations."""

import json
import hashlib
import time
from pathlib import Path
from typing import Any, Callable, Optional, Dict


class SetupCache:
    """Cache detection results and API calls for speed."""

    def __init__(self):
        self.cache_dir = Path.home() / ".conductor" / ".cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.memory_cache: Dict[str, Dict[str, Any]] = {}

    def get(self, key: str) -> Optional[Any]:
        """Get from memory cache first, then disk."""
        # Memory cache (fastest)
        if key in self.memory_cache:
            entry = self.memory_cache[key]
            if time.time() - entry["timestamp"] < entry["ttl"]:
                return entry["value"]

        # Disk cache (fast)
        cache_file = self.cache_dir / f"{key}.json"
        if cache_file.exists():
            try:
                data = json.loads(cache_file.read_text())
                if time.time() - data["timestamp"] < data["ttl"]:
                    # Populate memory cache
                    self.memory_cache[key] = data
                    return data["value"]
            except Exception:
                # Invalid cache file, ignore
                pass

        return None

    def set(self, key: str, value: Any, ttl: int = 3600) -> None:
        """Set in both memory and disk cache."""
        entry = {"value": value, "timestamp": time.time(), "ttl": ttl}

        # Memory cache
        self.memory_cache[key] = entry

        # Disk cache
        cache_file = self.cache_dir / f"{key}.json"
        try:
            cache_file.write_text(json.dumps(entry, indent=2))
        except Exception:
            # Ignore cache write failures
            pass

    def get_or_compute(self, key: str, compute_fn: Callable, ttl: int = 3600) -> Any:
        """Get from cache or compute and cache result."""
        cached = self.get(key)
        if cached is not None:
            return cached

        value = compute_fn()
        self.set(key, value, ttl)
        return value

    def clear(self) -> None:
        """Clear all caches."""
        self.memory_cache.clear()
        try:
            for cache_file in self.cache_dir.glob("*.json"):
                cache_file.unlink()
        except Exception:
            # Ignore cache clear failures
            pass

    def get_project_hash(self, project_root: Path) -> str:
        """Generate unique hash for project state."""
        key_files = [
            "package.json",
            "pyproject.toml",
            "Cargo.toml",
            "go.mod",
            "requirements.txt",
            "Gemfile",
            "pom.xml",
            "build.gradle",
        ]
        hasher = hashlib.md5()

        # Hash key files that define dependencies
        for file_name in key_files:
            file_path = project_root / file_name
            if file_path.exists():
                try:
                    hasher.update(file_path.read_bytes())
                except Exception:
                    # Ignore read errors
                    pass

        # Hash directory structure for better cache invalidation
        try:
            for p in sorted(project_root.rglob("*")):
                if p.is_file() and not any(
                    skip in str(p) for skip in [".git", "__pycache__", "node_modules"]
                ):
                    hasher.update(str(p.relative_to(project_root)).encode())
        except Exception:
            # Ignore traversal errors
            pass

        return hasher.hexdigest()[:12]


# Global cache instance
_cache = None


def get_cache() -> SetupCache:
    """Get global cache instance (singleton)."""
    global _cache
    if _cache is None:
        _cache = SetupCache()
    return _cache
