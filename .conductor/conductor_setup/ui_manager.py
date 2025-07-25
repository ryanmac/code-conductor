"""UI Manager for beautiful terminal experience with determinate progress bars."""

from rich.console import Console
from rich.theme import Theme
from rich.progress import (
    Progress,
    BarColumn,
    TextColumn,
    TimeRemainingColumn,
    TimeElapsedColumn,
)
from rich.table import Table
from rich import box
from typing import Optional, Dict, Any
import time


class UIManager:
    """Manages all UI interactions for fast, deterministic terminal experience."""

    def __init__(self):
        # Minimal theme - focus on clarity
        custom_theme = Theme(
            {
                "conductor.primary": "cyan",
                "conductor.success": "green",
                "conductor.warning": "yellow",
                "conductor.error": "red",
                "conductor.info": "dim",
            }
        )
        self.console = Console(theme=custom_theme)
        self.start_time = time.time()

    def show_welcome(self) -> None:
        """Display minimal welcome message - focus on speed."""
        self.console.print(
            "[conductor.primary]Code Conductor[/conductor.primary] - "
            "[conductor.info]60-second setup starting...[/conductor.info]\n"
        )

    def create_progress(self) -> Progress:
        """Create determinate progress bar for predictable operations."""
        return Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            TimeRemainingColumn(),
            console=self.console,
            expand=False,
        )

    def show_success(self, config: Dict[str, Any]) -> None:
        """Show modest success message with actionable next steps."""
        elapsed = int(time.time() - self.start_time)

        self.console.print(f"\n✓ Code Conductor configured in {elapsed} seconds\n")
        self.console.print(
            f"Stack detected: {config.get('stack_summary', 'Multiple technologies')}"
        )
        self.console.print(
            f"Agents ready: {len(config.get('roles', {}).get('specialized', []))} + dev"
        )
        self.console.print(f"First tasks: {config.get('task_count', 0)} available\n")
        self.console.print("Quick start:")
        self.console.print("   ./conductor start dev\n")
        self.console.print(
            "This creates your workspace in ~/worktrees/agent-dev-001/\n"
        )
        self.console.print("Next: Run 'conductor tasks' to see available work.")

    def show_error(
        self, title: str, message: str, recovery_hint: Optional[str] = None
    ) -> None:
        """Display error with optional recovery suggestion."""
        self.console.print(f"\n[conductor.error]{title}[/conductor.error]")
        self.console.print(f"{message}")
        if recovery_hint:
            self.console.print(
                f"\n[conductor.info]💡 Try: {recovery_hint}[/conductor.info]"
            )

    def show_detection_results(self, stack_info: Dict[str, Any]) -> None:
        """Display technology detection results in a clean table."""
        table = Table(box=box.SIMPLE, show_header=False)
        table.add_column("Category", style="conductor.primary")
        table.add_column("Detected")

        if stack_info.get("languages"):
            table.add_row("Languages", ", ".join(stack_info["languages"]))
        if stack_info.get("frameworks"):
            table.add_row("Frameworks", ", ".join(stack_info["frameworks"]))
        if stack_info.get("tools"):
            table.add_row("Build Tools", ", ".join(stack_info["tools"]))
        if stack_info.get("test_frameworks"):
            table.add_row("Testing", ", ".join(stack_info["test_frameworks"]))
        if stack_info.get("monorepo"):
            table.add_row("Structure", f"Monorepo ({stack_info['monorepo']['tool']})")

        self.console.print("\n", table, "\n")

    def prompt(self, message: str, default: Optional[str] = None) -> str:
        """Get user input with optional default value."""
        if default:
            prompt_text = f"{message} [{default}]: "
        else:
            prompt_text = f"{message}: "

        response = self.console.input(
            f"[conductor.primary]{prompt_text}[/conductor.primary]"
        )
        return response.strip() or default or ""

    def confirm(self, message: str, default: bool = True) -> bool:
        """Get yes/no confirmation with default value."""
        default_indicator = "Y/n" if default else "y/N"
        prompt = f"[conductor.primary]{message} [{default_indicator}]: "
        prompt += "[/conductor.primary]"
        response = self.console.input(prompt).lower().strip()

        if not response:
            return default
        return response in ("y", "yes")
