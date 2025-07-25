"""
Discovery Task Creation Module
Creates initialization task for AI agents to discover project structure
"""

import subprocess
from pathlib import Path
from typing import Optional


class DiscoveryTaskCreator:
    """Creates discovery task for project initialization"""

    def __init__(self, project_root: Path):
        self.project_root = project_root

    def create_discovery_task_if_needed(self) -> Optional[str]:
        """Create initialization task for AI agents to discover project structure"""

        # Check if project has substantial existing content
        if not self._should_create_discovery_task():
            print("\n📋 New project detected - skipping discovery task")
            return None

        # Check GitHub CLI availability
        if not self._check_github_cli_ready():
            return None

        print("\n📚 Existing project detected. Creating discovery task...")

        discovery_task_body = self._get_discovery_task_body()

        # Create the discovery task
        return self._create_github_issue(discovery_task_body)

    def _should_create_discovery_task(self) -> bool:
        """Determine if a discovery task should be created"""
        indicators = {
            "has_docs": any(
                (self.project_root / p).exists()
                for p in ["docs/", "README.md", "ARCHITECTURE.md"]
            ),
            "has_code": any(self.project_root.glob("**/*.py"))
            or any(self.project_root.glob("**/*.js")),
            "has_tests": (self.project_root / "tests").exists()
            or (self.project_root / "test").exists(),
        }
        return any(indicators.values())

    def _check_github_cli_ready(self) -> bool:
        """Check if GitHub CLI is available and authenticated"""
        # Check if GitHub CLI is available
        try:
            subprocess.run(["gh", "--version"], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("\n⚠️  GitHub CLI not available - skipping discovery task creation")
            return False

        # Check if authenticated
        try:
            subprocess.run(["gh", "auth", "status"], capture_output=True, check=True)
        except subprocess.CalledProcessError:
            print(
                "\n⚠️  GitHub CLI not authenticated - skipping discovery task creation"
            )
            return False

        return True

    def _create_github_issue(self, body: str) -> Optional[str]:
        """Create GitHub issue and return issue number"""
        try:
            result = subprocess.run(
                [
                    "gh",
                    "issue",
                    "create",
                    "--title",
                    "🔍 [INIT] Discover project documentation and create task map",
                    "--body",
                    body,
                    "--label",
                    "conductor:task,conductor:init,priority:critical,effort:medium",
                ],
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                issue_url = result.stdout.strip()
                issue_number = issue_url.split("/")[-1]
                print(f"✅ Created initialization task #{issue_number}")
                return issue_number
            else:
                print(f"⚠️  Could not create discovery task: {result.stderr}")
                return None
        except Exception as e:
            print(f"⚠️  Could not create discovery task: {e}")
            return None

    def _get_discovery_task_body(self) -> str:
        """Get the discovery task body content"""
        return """## 🔍 Documentation Discovery and Task Generation

**This is a special initialization task for AI agents to map the project and
create all subsequent tasks.**

## Your Mission

Investigate this repository to understand:
1. What the project does
2. What documentation exists
3. What's been implemented vs. what's still needed
4. What tasks should be created for other agents

## Step-by-Step Instructions

### 1. Explore Project Structure
```bash
# Get overview of the repository
find . -type f -name "*.md" | grep -v node_modules | head -20
ls -la docs/ doc/ documentation/ 2>/dev/null
tree -d -L 3 -I 'node_modules|.git|dist|build' 2>/dev/null || find . -type d | head -20

# Check for key files
cat README.md | head -50
cat package.json 2>/dev/null | jq '.name, .description, .scripts'
cat setup.py 2>/dev/null | head -20
```

### 2. Identify Documentation
Look for:
- README files at any level
- docs/ or documentation/ directories
- Architecture documents (ARCHITECTURE.md, DESIGN.md)
- API documentation (swagger, openapi files)
- Requirements or specifications
- Development guides (CONTRIBUTING.md, DEVELOPMENT.md)
- TODO files or ROADMAP documents

### 3. Analyze Implementation Status
```bash
# Check source code structure
find src/ -type f -name "*.py" -o -name "*.js" -o -name "*.ts" 2>/dev/null | head -20
find test/ tests/ -type f 2>/dev/null | head -10

# Look for TODO/FIXME comments
grep -r "TODO\\|FIXME\\|HACK\\|BUG" --include="*.py" --include="*.js" \\
    --include="*.ts" . | head -20

# Check test coverage if available
npm test -- --coverage 2>/dev/null || pytest --cov 2>/dev/null || \\
    echo "No coverage data"
```

### 4. Create Documentation Map

Create `.conductor/documentation-map.yaml` with this structure:

```yaml
# Project overview - REQUIRED
project:
  name: "[detect from package.json, setup.py, or README]"
  description: "[brief description of what this project does]"
  type: "[web-app|api|library|cli|mobile|desktop]"
  primary_language: "[python|javascript|typescript|go|rust|etc]"
  framework: "[react|django|express|etc]"
  status: "[prototype|development|beta|production]"
  estimated_completion: "[0-100]%"

# Documentation sources - Fill in what exists
documentation:
  readme:
    - path: "README.md"
      summary: "[what this README covers]"
      quality: "[excellent|good|needs-work|missing]"

  architecture:
    - path: "[path to architecture docs]"
      summary: "[what it describes]"
      decisions: "[list key architectural decisions]"

  api:
    - path: "[path to API docs]"
      format: "[openapi|swagger|markdown|other]"
      completeness: "[complete|partial|outdated|missing]"

  requirements:
    - path: "[path to requirements]"
      type: "[functional|technical|business]"
      status: "[current|outdated|draft]"

# Current implementation state
implementation:
  completed_features:
    - name: "[feature name]"
      description: "[what it does]"
      location: "[where in codebase]"
      has_tests: [true|false]
      documentation: "[documented|needs-docs|undocumented]"

  missing_features:
    - name: "[feature from requirements not yet started]"
      description: "[what it should do]"
      source_requirement: "[where this requirement comes from]"
      priority: "[critical|high|medium|low]"
      estimated_effort: "[small|medium|large]"

# Proposed tasks - MOST IMPORTANT SECTION
proposed_tasks:
  # Create 10-20 specific, actionable tasks based on your investigation
  - title: "[Clear, specific task title]"
    description: "[What needs to be done]"
    type: "[feature|bugfix|refactor|documentation|testing|deployment]"
    source_requirement: "[which doc/requirement this comes from]"
    estimated_effort: "[small|medium|large]"
    priority: "[critical|high|medium|low]"
    assigned_role: "[dev|frontend|backend|devops|etc]"
    success_criteria:
      - "[Specific, measurable criterion]"
      - "[Another criterion]"
    implementation_notes: "[Any helpful context for the implementer]"

# Summary for humans
summary:
  total_tasks: [number]
  critical_tasks: [number]
  estimated_total_effort: "[in ideal dev days]"
  recommended_next_steps:
    - "[First thing to do]"
    - "[Second thing to do]"
```

### 5. Validate Your Work

Before marking complete:
1. Ensure the YAML is valid: Run validation with:
   `python -c "import yaml; yaml.safe_load(open('.conductor/documentation-map.yaml'))"`
2. Check you've created at least 10 concrete tasks
3. Verify each task has clear success criteria
4. Make sure priorities are reasonable

## Success Criteria

- [ ] Created valid `.conductor/documentation-map.yaml`
- [ ] Identified all major documentation sources
- [ ] Assessed project completion percentage
- [ ] Created 10-20 specific, actionable tasks
- [ ] Each task has clear source documentation/requirements
- [ ] Tasks are properly prioritized
- [ ] Tasks have appropriate role assignments

## Completion

After creating the documentation map:
1. Run the task generator:
   `python .conductor/scripts/generate-tasks-from-map.py --auto`
2. Verify tasks were created: `gh issue list -l 'conductor:task' --limit 25`
3. Comment on this issue with a summary of tasks created
4. Mark this task complete using: `./conductor complete`

---
*This is a one-time initialization task. Once complete, all future work will be properly coordinated.*
"""
