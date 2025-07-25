# 🔧 Technical Implementation Guide - Setup Enhancements

## Priority 1: Determinate Progress System (Rich UI)

### Required Changes

**1. Add dependency to requirements.txt**:
```txt
rich>=13.7.0  # Beautiful terminal UI
```

**2. Update setup.py imports**:
```python
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.panel import Panel
from rich.tree import Tree
from rich.table import Table
from rich.syntax import Syntax
from rich import box
```

**3. Create UIManager class in conductor_setup/ui_manager.py**:
```python
from rich.console import Console
from rich.theme import Theme
from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn, TimeElapsedColumn
from typing import Optional, Dict, Any
import time

class UIManager:
    """Manages all UI interactions for fast, deterministic terminal experience."""
    
    def __init__(self):
        # Minimal theme - focus on clarity
        custom_theme = Theme({
            "conductor.primary": "cyan",
            "conductor.success": "green",
            "conductor.warning": "yellow",
            "conductor.error": "red",
            "conductor.info": "dim"
        })
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
            expand=False
        )
        
    def show_success(self, config: Dict[str, Any]) -> None:
        """Show modest success message with actionable next steps."""
        elapsed = int(time.time() - self.start_time)
        
        self.console.print(f"\n✓ Code Conductor configured in {elapsed} seconds\n")
        self.console.print(f"Stack detected: {config['stack_summary']}")
        self.console.print(f"Agents ready: {len(config['roles'])}")
        self.console.print(f"First tasks: {config['task_count']} available\n")
        self.console.print("Quick start:")
        self.console.print("   ./conductor start dev\n")
        self.console.print("This creates your workspace in ~/worktrees/agent-dev-001/\n")
        self.console.print("Next: Run 'conductor tasks' to see available work.")
```

**4. Update detector.py with determinate progress**:
```python
def detect_technology_stack(self, ui: Optional[UIManager] = None) -> Dict[str, Any]:
    """Detect technology stack with fast, cached results."""
    # Check cache first
    cache_key = self._get_project_hash()
    cached_result = self.cache.get(f"stack_{cache_key}")
    if cached_result:
        return cached_result
    
    if ui:
        with ui.create_progress() as progress:
            # Total of 5 detection phases
            task = progress.add_task("Analyzing project", total=5)
            
            # Phase 1: Package managers (fast)
            progress.update(task, advance=1, description="Detecting package managers...")
            package_managers = self._detect_package_managers()
            
            # Phase 2: Frameworks (medium)
            progress.update(task, advance=1, description="Identifying frameworks...")
            frameworks = self._detect_frameworks()
            
            # Phase 3: Modern tools (medium)
            progress.update(task, advance=1, description="Checking modern tooling...")
            modern_tools = self._detect_modern_frameworks()
            
            # Phase 4: Test frameworks (fast)
            progress.update(task, advance=1, description="Finding test frameworks...")
            test_frameworks = self._detect_test_frameworks()
            
            # Phase 5: Monorepo setup (fast)
            progress.update(task, advance=1, description="Analyzing project structure...")
            monorepo = self._detect_monorepo_setup()
            
    # Compile results
    result = {
        "package_managers": package_managers,
        "frameworks": frameworks,
        "modern_tools": modern_tools,
        "test_frameworks": test_frameworks,
        "monorepo": monorepo
    }
    
    # Cache for next time
    self.cache.set(f"stack_{cache_key}", result, ttl=86400)
    return result
```

## Priority 2: Enhanced Technology Detection

### New Detections to Add

**1. Modern Framework Detection in detector.py**:
```python
def _detect_modern_frameworks(self) -> Dict[str, Any]:
    """Detect modern web frameworks and tools."""
    detections = {}
    
    # Vite-based projects
    vite_config_files = ["vite.config.js", "vite.config.ts", "vite.config.mjs"]
    for config_file in vite_config_files:
        if self._file_exists(config_file):
            detections["build_tool"] = "vite"
            detections["modern_tooling"] = True
            
            # Read config to detect framework
            config_content = self._read_file(config_file)
            if "@vitejs/plugin-react" in config_content:
                detections["framework_plugin"] = "react"
            elif "@vitejs/plugin-vue" in config_content:
                detections["framework_plugin"] = "vue"
            elif "@sveltejs/vite-plugin-svelte" in config_content:
                detections["framework_plugin"] = "svelte"
    
    # Remix detection
    if self._file_exists("remix.config.js"):
        detections["framework"] = "remix"
        detections["fullstack"] = True
        
    # Astro detection
    if self._file_exists("astro.config.mjs"):
        detections["framework"] = "astro"
        detections["static_site_generator"] = True
        
    # SvelteKit detection  
    if self._file_exists("svelte.config.js"):
        config_content = self._read_file("svelte.config.js")
        if "@sveltejs/kit" in config_content:
            detections["framework"] = "sveltekit"
            detections["fullstack"] = True
            
    # Nuxt 3 detection
    if self._file_exists("nuxt.config.ts"):
        detections["framework"] = "nuxt3"
        detections["fullstack"] = True
        
    return detections
```

**2. Monorepo Detection**:
```python
def _detect_monorepo_setup(self) -> Dict[str, Any]:
    """Detect monorepo tools and structure."""
    monorepo_info = {}
    
    # pnpm workspaces
    if self._file_exists("pnpm-workspace.yaml"):
        monorepo_info["tool"] = "pnpm"
        workspace_content = self._read_file("pnpm-workspace.yaml")
        # Parse workspace packages
        monorepo_info["workspace_count"] = len(self._parse_yaml_list(workspace_content))
        
    # Nx monorepo
    elif self._file_exists("nx.json"):
        monorepo_info["tool"] = "nx"
        nx_config = self._read_json("nx.json")
        monorepo_info["workspace_count"] = len(nx_config.get("projects", {}))
        
    # Lerna
    elif self._file_exists("lerna.json"):
        monorepo_info["tool"] = "lerna"
        lerna_config = self._read_json("lerna.json")
        monorepo_info["workspace_count"] = len(lerna_config.get("packages", []))
        
    # Rush
    elif self._file_exists("rush.json"):
        monorepo_info["tool"] = "rush"
        
    return monorepo_info
```

**3. Test Framework Detection**:
```python
def _detect_test_frameworks(self) -> List[str]:
    """Detect testing frameworks in use."""
    test_frameworks = []
    
    # JavaScript/TypeScript testing
    if self._file_exists("jest.config.js") or self._file_exists("jest.config.ts"):
        test_frameworks.append("jest")
    
    if self._file_exists("vitest.config.ts"):
        test_frameworks.append("vitest")
        
    if self._file_exists("cypress.config.js"):
        test_frameworks.append("cypress")
        
    if self._file_exists("playwright.config.ts"):
        test_frameworks.append("playwright")
        
    # Python testing
    if self._file_exists("pytest.ini") or self._file_exists("setup.cfg"):
        content = self._read_file("setup.cfg") if self._file_exists("setup.cfg") else ""
        if "[tool:pytest]" in content or self._file_exists("pytest.ini"):
            test_frameworks.append("pytest")
            
    # Check package.json for test runners
    if self._file_exists("package.json"):
        package_json = self._read_json("package.json")
        dev_deps = package_json.get("devDependencies", {})
        
        test_runners = {
            "@testing-library/react": "testing-library",
            "mocha": "mocha",
            "jasmine": "jasmine",
            "ava": "ava"
        }
        
        for package, framework in test_runners.items():
            if package in dev_deps:
                test_frameworks.append(framework)
                
    return test_frameworks
```

## Priority 3: Express Setup by Default

### Implementation in config_manager.py

```python
# Define express configurations with stack patterns
EXPRESS_CONFIGS = {
    "react-typescript": {
        "patterns": ["react", "typescript", "tsx"],
        "roles": {
            "default": "dev",
            "specialized": ["frontend", "code-reviewer"]
        },
        "github_integration": {
            "issue_to_task": True,
            "pr_reviews": True
        },
        "build_validation": ["npm test", "npm run build"],
        "suggested_tasks": [
            "Set up component testing with React Testing Library",
            "Add Storybook for component development",
            "Configure ESLint and Prettier"
        ]
    },
    "python-fastapi": {
        "patterns": ["fastapi", "python", "uvicorn"],
        "roles": {
            "default": "dev",
            "specialized": ["backend", "code-reviewer"]
        },
        "github_integration": {
            "issue_to_task": True,
            "pr_reviews": True
        },
        "build_validation": ["pytest", "black --check ."],
        "suggested_tasks": [
            "Add API documentation with OpenAPI",
            "Set up database migrations with Alembic",
            "Add integration tests for endpoints"
        ]
    },
    "nextjs-fullstack": {
        "patterns": ["next", "react", "node"],
        "roles": {
            "default": "dev",
            "specialized": ["frontend", "backend", "code-reviewer"]
        },
        "github_integration": {
            "issue_to_task": True,
            "pr_reviews": True
        },
        "build_validation": ["npm test", "npm run build", "npm run lint"],
        "suggested_tasks": [
            "Set up authentication with NextAuth.js",
            "Configure Prisma for database access",
            "Add E2E tests with Playwright"
        ]
    }
}

def get_express_config(self, stack_info: Dict) -> Optional[Dict]:
    """Match detected stack to express config."""
    detected_items = set()
    detected_items.update(stack_info.get("frameworks", []))
    detected_items.update(stack_info.get("languages", []))
    detected_items.update(stack_info.get("tools", []))
    
    # Find best match
    best_match = None
    best_score = 0
    
    for stack_name, config in EXPRESS_CONFIGS.items():
        score = len(detected_items.intersection(config["patterns"]))
        if score > best_score:
            best_match = stack_name
            best_score = score
    
    return EXPRESS_CONFIGS.get(best_match) if best_match else None

def gather_configuration(self, stack_info: Dict, ui: UIManager) -> Dict[str, Any]:
    """Gather config with express-by-default approach."""
    # Try express config first
    express_config = self.get_express_config(stack_info)
    
    if express_config:
        # Express setup - no questions asked
        ui.console.print(f"\nDetected {stack_info['primary_stack']} project - applying optimal configuration...")
        
        with ui.create_progress() as progress:
            task = progress.add_task("Configuring", total=3)
            
            progress.update(task, advance=1, description="Setting up roles...")
            # Apply roles from express config
            
            progress.update(task, advance=1, description="Enabling integrations...")
            # Apply GitHub settings
            
            progress.update(task, advance=1, description="Creating starter tasks...")
            # Generate tasks
            
        # Return complete config without any prompts
        return {
            "project_name": self._infer_project_name(),
            **express_config,
            "stack_info": stack_info,
            "setup_mode": "express"
        }
    else:
        # Only fall back to interactive for unknown stacks
        ui.console.print("\nUnique project structure detected - let's configure together...")
        return self._interactive_setup(stack_info, ui)
```

## Priority 4: Interactive Preview

### Implementation in validator.py

```python
def show_setup_preview(self, config: Dict[str, Any], ui: UIManager) -> None:
    """Show interactive preview of what will be created."""
    
    # Create file tree
    tree = Tree("📁 [conductor.primary]Your Code Conductor Setup[/conductor.primary]")
    
    # .conductor directory
    conductor_dir = tree.add("📁 .conductor/")
    conductor_dir.add("📄 config.yaml [conductor.info](Your project configuration)[/conductor.info]")
    conductor_dir.add(f"📝 CLAUDE.md [conductor.info](AI instructions for {config['technology_stack']['primary']})[/conductor.info]")
    
    # Roles
    roles_dir = conductor_dir.add("📁 roles/")
    for role in config['roles']['all']:
        icon = self._get_role_icon(role)
        roles_dir.add(f"{icon} {role}.md")
    
    # Scripts
    scripts_dir = conductor_dir.add("📁 scripts/")
    scripts_dir.add("🔧 conductor [conductor.info](Universal agent command)[/conductor.info]")
    scripts_dir.add("📋 task-claim.py")
    scripts_dir.add("🏥 health-check.py")
    
    # GitHub workflows
    github_dir = tree.add("📁 .github/workflows/")
    github_dir.add("⚙️ conductor.yml [conductor.info](Automation & monitoring)[/conductor.info]")
    github_dir.add("🔍 pr-review.yml [conductor.info](AI code reviews)[/conductor.info]")
    
    # Tasks
    if config.get('starter_tasks'):
        tasks_node = tree.add(f"📋 {len(config['starter_tasks'])} starter tasks ready!")
    
    ui.console.print("\n", tree, "\n")
    
    # Show feature summary
    features = Table(title="✨ Enabled Features", box=box.ROUNDED)
    features.add_column("Feature", style="conductor.primary")
    features.add_column("Status", justify="center")
    features.add_column("Details")
    
    features.add_row(
        "Concurrent Agents",
        "✅",
        f"Up to {config.get('max_concurrent_agents', 3)} agents working in parallel"
    )
    features.add_row(
        "GitHub Integration", 
        "✅",
        "Issues → Tasks, No token required"
    )
    features.add_row(
        "AI Code Reviews",
        "✅" if config['github_integration']['pr_reviews'] else "⏸️",
        "Opt-in reviews with /conductor review"
    )
    features.add_row(
        "Auto-Detection",
        "✅",
        f"Detected: {', '.join(config['technology_stack']['detected'])}"
    )
    
    ui.console.print(features)
    
def _get_role_icon(self, role: str) -> str:
    """Get emoji icon for role."""
    icons = {
        "dev": "🤖",
        "frontend": "🎨", 
        "backend": "⚙️",
        "devops": "🔧",
        "security": "🔒",
        "mobile": "📱",
        "ml-engineer": "🧠",
        "data": "📊",
        "code-reviewer": "🔍"
    }
    return icons.get(role, "📄")
```

## Priority 5: Smart Error Recovery

### Create conductor_setup/error_handler.py

```python
from typing import Dict, Optional, Callable
from rich.console import Console
from rich.panel import Panel
import subprocess
import sys

class SmartErrorHandler:
    """Intelligent error handling with automatic recovery suggestions."""
    
    def __init__(self, console: Console):
        self.console = console
        self.recovery_strategies = {
            "GitHubAuthError": self._handle_github_auth,
            "PythonVersionError": self._handle_python_version,
            "GitNotFoundError": self._handle_git_missing,
            "PermissionError": self._handle_permission_error,
            "NetworkError": self._handle_network_error
        }
        
    def handle_error(self, error: Exception, context: str) -> bool:
        """Handle error with smart recovery. Returns True if recovered."""
        error_type = type(error).__name__
        
        if error_type in self.recovery_strategies:
            return self.recovery_strategies[error_type](error, context)
        else:
            return self._handle_generic_error(error, context)
            
    def _handle_github_auth(self, error: Exception, context: str) -> bool:
        """Handle GitHub authentication errors."""
        self.console.print(Panel(
            "[conductor.error]🔐 GitHub Authentication Required[/conductor.error]\n\n"
            "Code Conductor needs GitHub access to manage tasks.\n"
            "Let's fix this in 30 seconds:\n\n"
            "1. I'll open GitHub authentication for you\n"
            "2. Login with your GitHub account\n"
            "3. Return here when complete\n",
            title="Quick Fix Available",
            border_style="conductor.warning"
        ))
        
        if self.console.input("\n[conductor.primary]Ready to authenticate? [Y/n]:[/conductor.primary] ").lower() != 'n':
            try:
                subprocess.run(["gh", "auth", "login", "--web"], check=True)
                self.console.print("\n[conductor.success]✅ Authentication successful![/conductor.success]")
                return True
            except:
                self.console.print("\n[conductor.error]Please run: gh auth login[/conductor.error]")
                return False
                
    def _handle_python_version(self, error: Exception, context: str) -> bool:
        """Handle Python version compatibility issues."""
        current_version = sys.version_info
        
        self.console.print(Panel(
            f"[conductor.error]🐍 Python Version Issue[/conductor.error]\n\n"
            f"Current: Python {current_version.major}.{current_version.minor}.{current_version.micro}\n"
            f"Required: Python 3.9 - 3.12\n\n"
            f"Quick fixes:\n"
            f"  • pyenv: pyenv install 3.11 && pyenv local 3.11\n"
            f"  • conda: conda create -n conductor python=3.11\n"
            f"  • brew: brew install python@3.11\n",
            title="Version Mismatch",
            border_style="conductor.warning"
        ))
        return False
```

## Priority 6: Aggressive Caching System

### Create conductor_setup/cache_manager.py

```python
import json
import hashlib
import time
from pathlib import Path
from typing import Any, Callable, Optional, Dict

class SetupCache:
    """High-performance cache for all setup operations."""
    
    def __init__(self):
        self.cache_dir = Path.home() / ".conductor" / ".cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.memory_cache: Dict[str, Dict[str, Any]] = {}
        
    def get(self, key: str) -> Optional[Any]:
        """Get from memory cache first, then disk."""
        # Memory cache (fastest)
        if key in self.memory_cache:
            entry = self.memory_cache[key]
            if time.time() - entry['timestamp'] < entry['ttl']:
                return entry['value']
        
        # Disk cache (fast)
        cache_file = self.cache_dir / f"{key}.json"
        if cache_file.exists():
            try:
                data = json.loads(cache_file.read_text())
                if time.time() - data['timestamp'] < data['ttl']:
                    # Populate memory cache
                    self.memory_cache[key] = data
                    return data['value']
            except:
                pass
        
        return None
    
    def set(self, key: str, value: Any, ttl: int = 3600) -> None:
        """Set in both memory and disk cache."""
        entry = {
            'value': value,
            'timestamp': time.time(),
            'ttl': ttl
        }
        
        # Memory cache
        self.memory_cache[key] = entry
        
        # Disk cache
        cache_file = self.cache_dir / f"{key}.json"
        cache_file.write_text(json.dumps(entry, indent=2))
    
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
        for cache_file in self.cache_dir.glob("*.json"):
            cache_file.unlink()

# Global cache instance
_cache = SetupCache()

def get_cache() -> SetupCache:
    """Get global cache instance."""
    return _cache
```

### Cache Integration Points

```python
# In detector.py
def __init__(self, project_root: Path):
    self.project_root = project_root
    self.cache = get_cache()
    
def _get_project_hash(self) -> str:
    """Generate unique hash for project state."""
    key_files = ['package.json', 'pyproject.toml', 'Cargo.toml', 'go.mod']
    hasher = hashlib.md5()
    
    for file in key_files:
        file_path = self.project_root / file
        if file_path.exists():
            hasher.update(file_path.read_bytes())
    
    return hasher.hexdigest()[:12]

# In github_integration.py
def check_github_labels(self, repo: str) -> Dict[str, bool]:
    """Check GitHub labels with caching."""
    return self.cache.get_or_compute(
        f"github_labels_{repo}",
        lambda: self._fetch_github_labels(repo),
        ttl=3600  # 1 hour cache
    )

# In config_manager.py
def detect_common_patterns(self) -> Dict[str, Any]:
    """Detect common project patterns with caching."""
    return self.cache.get_or_compute(
        f"patterns_{self.project_hash}",
        lambda: self._analyze_project_patterns(),
        ttl=86400  # 24 hour cache
    )
```

## Priority 7: Performance Optimizations

### Parallel Operations

```python
# In setup.py
import concurrent.futures
from typing import List, Callable, Any

def run_parallel_tasks(tasks: List[Callable[[], Any]], ui: UIManager) -> List[Any]:
    """Run multiple tasks in parallel with progress tracking."""
    results = []
    
    with ui.create_progress() as progress:
        main_task = progress.add_task("Setting up", total=len(tasks))
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(task) for task in tasks]
            
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                results.append(result)
                progress.update(main_task, advance=1)
    
    return results

# Usage
tasks = [
    lambda: detector.detect_technology_stack(),
    lambda: github.check_authentication(),
    lambda: validator.check_python_version(),
    lambda: file_gen.prepare_templates()
]

results = run_parallel_tasks(tasks, ui)
```

## Next Steps

1. **Implementation Priority**:
   - Day 1: Rich UI with determinate progress
   - Day 2: Caching system
   - Day 3: Express-by-default setup
   - Day 4: Enhanced detection accuracy
   - Day 5: Performance optimization

2. **Testing Strategy**:
   - Unit tests for cache manager
   - Integration tests for express setup
   - Performance benchmarks for 60-second goal
   - User acceptance testing

3. **Monitoring**:
   - Setup completion time tracking
   - Cache hit rate monitoring
   - Error recovery success rate
   - User satisfaction metrics

These implementations focus on speed, reliability, and user experience to achieve the 60-second setup goal and NPS >80.