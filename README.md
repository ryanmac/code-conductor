# 🎼 Conductor's Score

<img width="1024" height="1024" alt="image" src="https://github.com/user-attachments/assets/09dea359-56a0-4c65-8c16-b98ec2b4f02a" />

**Transform your development workflow in 60 seconds.** From tweet discovery to AI agents shipping code—the GitHub-native coordination system that changes how you build.

> *"Stop juggling tasks. Start orchestrating agents."*

## 🚀 **Why Developers Are Switching to Agentic Development**

- ⚡ **Focus on architecture, let agents handle implementation** - Spend time on what matters most
- 🎯 **Zero config for 90% of projects** - Auto-detects your stack and configures optimal roles
- 🔒 **AI code reviews on every PR** - Built-in CodeRabbit-style reviews catch bugs before merge
- 🤖 **Smart agent roles** - Generalist "dev" handles most tasks, specialists for complex work
- 📊 **Native GitHub integration** - Issues become tasks, Actions monitor health
- 🔄 **Self-healing coordination** - Automatic cleanup, heartbeat monitoring, stale work recovery

*"From weekend side project to shipping product in weeks, not months."*

## 🎯 **90% Stack Coverage - Your Tech is Supported**

Conductor-Score automatically detects and configures for the most popular technology stacks:

### **Frontend & Full-Stack** (40% of projects)
- **React/Next.js** - Auto-configures frontend & UI roles
- **Vue/Nuxt** - Component-based development ready
- **Angular** - Enterprise app support
- **Svelte/SvelteKit** - Modern reactive apps

### **Backend & APIs** (35% of projects)
- **Node.js** (Express, NestJS) - Microservices ready
- **Python** (Django, Flask, FastAPI) - Web & ML support
- **Go** (Gin, Echo, Fiber) - High-performance services
- **Java/Kotlin** (Spring) - Enterprise backends
- **PHP** (Laravel, Symfony) - Rapid development
- **.NET Core** (ASP.NET) - Microsoft stack

### **Mobile & Desktop** (15% of projects)
- **React Native** - Cross-platform mobile
- **Flutter** - Native performance
- **Tauri** - Lightweight desktop apps
- **Electron** - Web-powered desktop

### **Specialized Roles Auto-Configured**
Based on your stack, we automatically add:
- 🤖 **code-reviewer** - AI reviews on every PR (always included)
- 🎨 **frontend** - UI/UX implementation
- 📱 **mobile** - Platform-specific features
- 🔧 **devops** - CI/CD & infrastructure
- 🔒 **security** - Vulnerability scanning
- 🧮 **ml-engineer** - ML model deployment
- 📊 **data** - ETL & analytics

## ⚡ **60-Second Setup**

**One command. Instant AI coordination.**

**Prerequisites for all options:** Git, Python 3.9-3.12, curl (for one-liner), and tar. Run from the root of an existing Git repository. **If using pyenv, ensure your active Python version (e.g., via `pyenv shell 3.12.x`) has Poetry installed if you prefer it; otherwise, the script falls back to pip.**

### **Option 1: Universal One-Liner (Recommended - No Cloning Required)**
Run this in your existing project's root directory to download and install Conductor-Score directly:

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/ryanmac/conductor-score/main/conductor-init.sh)
```

- This method avoids cloning the full Conductor-Score repo and is ideal for integrating into existing projects without repository pollution.
- The script will prompt before overwriting any existing installation.
- **Security best practice:** Review the script at the raw URL before running.
- **Pyenv users:** If Poetry install fails, switch to the Python version that has Poetry installed (e.g., `pyenv shell 3.10.13`) and re-run.

<img width="1084" height="350" alt="One-line Install" src="https://github.com/user-attachments/assets/3a04506f-982f-457a-b8ea-98b6448c0219" />
<img width="1084" height="540" alt="Happy orchestrating" src="https://github.com/user-attachments/assets/1c7bb744-1194-471f-a12c-9672d208dbf3" />


### Option 2: Poetry (For Cloned Repo)
```bash
# Clone the repository
git clone https://github.com/ryanmac/conductor-score.git
cd conductor-score

# Install with Poetry (auto-creates virtual environment)
poetry install
poetry run python setup.py
```

### Option 3: Pip + Virtual Environment (For Cloned Repo)
```bash
# Clone the repository
git clone https://github.com/ryanmac/conductor-score.git
cd conductor-score

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run setup
python setup.py
```

### Option 4: One-Command Install Script (For Cloned Repo)
```bash
# From the repository directory:
./install.sh

# Or with custom setup options:
./install.sh --auto
```

**That's it.** Now create a GitHub Issue with `conductor:task` label, launch an agent via [Conductor.build](https://conductor.build) (macOS only as of 2024-07-22) or terminal workflow (all platforms), and watch it work.

## How It Works

1. **Setup Phase**: Use the universal installer (Option 1) or other setup methods to configure your project. The setup script detects your project type and configures roles.
2. **Task Creation**: Create tasks via GitHub Issues or directly in the state file
3. **Agent Initialization**: Agents use the universal bootstrap to claim work
4. **Isolated Development**: Each agent works in a git worktree to prevent conflicts
5. **Automated Coordination**: GitHub Actions manage health, cleanup, and task flow

## Architecture

### Hybrid Role Model

The system uses a hybrid approach optimized for efficiency:

- **Default Role**: `dev` - A generalist that can handle any task without specific requirements
- **Specialized Roles**: Optional roles like `devops`, `security` for complex domains

This reduces the complexity of managing many agent types while maintaining quality for specialized work.

### File Structure

```
.conductor/
├── config.yaml           # Project configuration with auto-detected stack
├── workflow-state.json   # Central coordination state
├── roles/               # Role definitions
│   ├── dev.md          # Default generalist
│   ├── code-reviewer.md # AI-powered PR reviewer
│   ├── frontend.md     # UI/UX specialist
│   ├── mobile.md       # Mobile app developer
│   ├── devops.md       # CI/CD specialist
│   ├── security.md     # Security specialist
│   ├── ml-engineer.md  # ML/AI specialist
│   └── data.md         # Data engineer
├── scripts/            # Automation scripts
│   ├── bootstrap.sh    # Universal agent init
│   ├── task-claim.py   # Atomic task assignment
│   ├── code-reviewer.py # AI code review engine
│   └── health-check.py # System monitoring
└── examples/           # Stack-specific task templates
    ├── nextjs-webapp/
    ├── python-webapp/
    ├── mobile-app/
    └── ...
```

## Configuration

### Project Setup

Run `python setup.py` to configure:

- Project name and documentation location
- Technology stack detection
- Role selection (hybrid model)
- Task management approach
- GitHub integration settings

### Role Definitions

Each role has a Markdown file in `.conductor/roles/` defining:

- Responsibilities
- Task selection criteria
- Required skills
- Success metrics

### Task Format

Tasks include complete specifications:

```json
{
  "id": "task_001",
  "title": "Implement authentication",
  "specs": "docs/auth-spec.md",
  "best_practices": ["Use JWT", "Implement refresh tokens"],
  "success_criteria": {
    "tests": "100% coverage",
    "security": "Pass security scan"
  },
  "required_skills": [],  // Empty = any dev can take it
  "estimated_effort": "medium"
}
```

## 🤖 AI Code Review - Built-In Quality Gates

Every pull request automatically gets AI-powered code reviews that:

- 🔒 **Security scanning** - Catches hardcoded secrets, SQL injection risks, unsafe operations
- 🐛 **Bug detection** - Identifies logic errors, null pointer risks, race conditions
- 💡 **Improvement suggestions** - Performance optimizations, better patterns, refactoring opportunities
- 🎨 **Style consistency** - Ensures coding standards across the team
- 🧪 **Test coverage** - Suggests missing tests and edge cases

### How It Works

1. **Automatic trigger** - Reviews start instantly on PR creation/update
2. **Contextual analysis** - Understands your codebase patterns
3. **Actionable feedback** - Clear, specific suggestions with examples
4. **Zero configuration** - Works out of the box with your existing GitHub workflow

```yaml
# .github/workflows/code-review.yml (auto-created)
name: AI Code Review
on:
  pull_request:
    types: [opened, synchronize, reopened]
```

## Agent Workflow

### Launching an Agent

**Option A: Conductor Desktop App (macOS only)**
```bash
export AGENT_ROLE=dev  # or devops, security, etc.
bash .conductor/scripts/bootstrap.sh
# Follow the printed instructions to open in Conductor app
```

**Option B: Multiple Terminals (All Platforms)**
```bash
bash .conductor/scripts/bootstrap.sh dev
cd worktrees/agent-dev-[task_id]
# Use tmux or screen for session management on Linux/Windows
# Start your Claude Code session in the worktree
```

📚 **[See complete usage guide →](docs/USAGE.md)**

### Agent Lifecycle

1. **Initialize**: Load role definition and check dependencies
2. **Claim Task**: Atomically claim an available task
3. **Create Worktree**: Isolated git workspace for conflict-free work
4. **Execute Task**: Follow specifications and success criteria
5. **Report Status**: Update heartbeat and progress
6. **Complete/Idle**: Mark complete or report idle for cleanup

### Universal Bootstrap Prompt

The system provides a single prompt that works for any agent:

```
You are a Claude Code agent in a conductor-score coordinated project.
ROLE: {role}
PROJECT: {project_name}

1. Read your role definition: .conductor/roles/{role}.md
2. Check system state: .conductor/workflow-state.json
3. Claim a task: python .conductor/scripts/task-claim.py --role {role}
4. Work in your isolated worktree
5. Commit and push changes when complete

Note: Heartbeats are automatically managed by GitHub Actions.
```

## GitHub Integration

### Issues as Tasks

Create issues with the `conductor:task` label to automatically convert them to tasks.

### Automated Workflows

- **Health Monitoring**: Every 15 minutes
- **Stale Cleanup**: Removes abandoned work
- **Task Scheduling**: Processes dependencies
- **Status Reports**: Updates dashboard issue

## Monitoring

### System Health

```bash
# Check local status
python .conductor/scripts/health-check.py

# View GitHub dashboard
# Check issue with 'conductor:status' label
```

### Metrics Tracked

- Active agents and their tasks
- Available task queue depth
- Completion rate and velocity
- System health indicators

## Examples

### 🌟 **Works with Your Stack**

<details>
<summary><strong>React Web App</strong> - Modern full-stack development</summary>

```yaml
project_name: harmony-webapp
roles:
  default: dev
  specialized: [devops, ui-designer]
build_validation:
  - npm test -- --coverage
  - npm run lint
  - npm run build
```
</details>

<details>
<summary><strong>Chrome Extension + NextJS</strong> - Browser extension with web dashboard</summary>

```yaml
project_name: symphony-extension
roles:
  default: dev
  specialized: [devops]
protected_files:
  - packages/extension/manifest.json
```
</details>

<details>
<summary><strong>Python Microservices</strong> - Scalable backend architecture</summary>

```yaml
project_name: api-platform
roles:
  default: dev
  specialized: [devops, security]
quality_checks:
  - pytest --cov=services
  - bandit -r services/
```
</details>

<details>
<summary><strong>Tauri Desktop App</strong> - Cross-platform Rust + JS application</summary>

```yaml
project_name: desktop-app
roles:
  default: dev
  specialized: [devops, security, rust-dev]
matrix_builds: [ubuntu, macos, windows]
```
</details>

**Don't see your stack?** [Contribute an example](CONTRIBUTING.md) and help other developers!

## Troubleshooting

### Common Issues

**No tasks available**
- Check `.conductor/workflow-state.json` has tasks
- Verify no file conflicts blocking tasks
- Create new tasks via GitHub issues

**Agent can't claim tasks**
- Run `python .conductor/scripts/dependency-check.py`
- Ensure GitHub CLI is authenticated: `gh auth status`
- Check git repository is clean: `git status`

**File conflicts**
- System prevents these automatically
- If occurs, check worktree isolation
- Run cleanup: `python .conductor/scripts/cleanup-stale.py`

### Debug Commands

```bash
# Check dependencies
python .conductor/scripts/dependency-check.py

# View system state
cat .conductor/workflow-state.json | jq

# Force cleanup
python .conductor/scripts/cleanup-stale.py --timeout 0

# Validate configuration
python .conductor/scripts/validate-config.py
```

## Storage Footprint

**Disk Usage**: Each agent creates a Git worktree (~50-200MB depending on project size)
- **Cleanup**: Run `gtclean` weekly to remove abandoned worktrees
- **Monitor**: Use `gtw` to list active worktrees
- **Automatic**: Stale worktrees (>7 days inactive) are auto-archived via GitHub Actions

**Pro tip**: Large projects should set `worktree_retention_days: 3` in config.yaml

## Best Practices

1. **Task Design**: Make tasks self-contained with clear specs
2. **Role Selection**: Start with dev-only, add specializations as needed
3. **Regular Cleanup**: Let automation handle stale work
4. **Monitor Health**: Check status issue regularly
5. **Incremental Adoption**: Start small, expand as comfortable

## Development Setup

### Prerequisites
- Python 3.9-3.12
- Git
- GitHub CLI (optional, for issue integration)

### Local Development
```bash
# Clone and setup
git clone https://github.com/ryanmac/conductor-score.git
cd conductor-score

# Install with Poetry (recommended)
poetry install

# Or with pip
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Run tests
poetry run pytest tests/ -v
# or
python -m pytest tests/ -v

# Run linting
poetry run flake8 .conductor/scripts/ setup.py
poetry run black --check .conductor/scripts/ setup.py
```

### CI/CD
The project uses GitHub Actions for continuous integration:
- **Linting**: flake8 and black formatting checks
- **Testing**: pytest on multiple Python versions (3.9, 3.10, 3.11, 3.12)
- **Security**: safety vulnerability scanning
- **Platforms**: Ubuntu and macOS

## Contributing

This is a template repository. To contribute:

1. Fork and improve
2. Test with your project type
3. Submit PRs with examples
4. Share your adaptations

### Development Guidelines
- Follow PEP 8 style guidelines
- Add tests for new functionality
- Update documentation for changes
- Ensure CI passes before submitting PRs

## License

MIT - See LICENSE file

## Support

- 🐛 [Issue Tracker](https://github.com/ryanmac/conductor-score/issues)
- 💬 [Discussions](https://github.com/ryanmac/conductor-score/discussions)

## 💬 **Join the Community**

- 🐛 **Found a bug?** [Report it](https://github.com/ryanmac/conductor-score/issues)
- 💡 **Have an idea?** [Start a discussion](https://github.com/ryanmac/conductor-score/discussions)
- 🛠️ **Want to contribute?** [See our guide](CONTRIBUTING.md)
- 𝕏 **Share your success** Mention [@ryanmac](https://x.com/ryanmac) with #ConductorScore

**Built for [Conductor.build](https://conductor.build) and [Warp](https://www.warp.dev/) users who refuse to juggle tasks manually.**

*Transform your development workflow. One command. Infinite possibilities.* 🎼
