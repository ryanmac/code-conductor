"""
Base detector class with common functionality
"""

import subprocess
from pathlib import Path
from typing import List, Optional


class BaseDetector:
    """Base class for all technology detectors"""

    def __init__(self, project_root: Path, debug: bool = False):
        self.project_root = project_root
        self.debug = debug

    def file_exists(self, *paths: str) -> bool:
        """Check if any of the given file paths exist"""
        for path in paths:
            if (self.project_root / path).exists():
                return True
        return False

    def glob_exists(self, pattern: str) -> bool:
        """Check if files matching the pattern exist"""
        return bool(list(self.project_root.glob(pattern)))

    def run_command(self, cmd: List[str], cwd: Optional[Path] = None) -> Optional[str]:
        """Run a command and return output, or None on error"""
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=cwd or self.project_root,
                check=False,
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except (subprocess.SubprocessError, FileNotFoundError):
            pass
        return None

    def read_file_lines(self, path: str, limit: int = 100) -> List[str]:
        """Read first N lines of a file safely"""
        file_path = self.project_root / path
        if not file_path.exists():
            return []

        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                lines = []
                for i, line in enumerate(f):
                    if i >= limit:
                        break
                    lines.append(line.strip())
                return lines
        except Exception:
            return []

    def detect(self) -> List[str]:
        """Override this method in subclasses"""
        raise NotImplementedError("Subclasses must implement detect()")
