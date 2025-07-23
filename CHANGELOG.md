# Changelog

All notable changes to Code Conductor will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- 🎯 **90% Stack Coverage**: Enhanced detection for 10 major technology clusters covering 90% of real-world projects
  - React/Next.js, Vue/Nuxt, Angular, Svelte full-stack applications
  - Node.js, Python, Go, Java/Kotlin, PHP, .NET Core backends
  - React Native, Flutter mobile development
  - Tauri, Electron desktop applications
- 🤖 **AI Code Reviewer**: Built-in CodeRabbit-style PR reviews for all projects
  - Automatic security vulnerability detection
  - Bug and logic error identification
  - Code quality and performance suggestions
  - Test coverage recommendations
  - GitHub workflow included (`.github/workflows/code-review.yml`)
- 🎭 **Enhanced Role System**: New specialized roles based on detected stack
  - `code-reviewer` - AI-powered PR reviews (always included)
  - `frontend` - React, Vue, Angular specialists
  - `mobile` - React Native, Flutter developers
  - `data` - Data pipeline and analytics engineers
- 📊 **Interactive Setup**: Post-installation role configuration
  - Shows detected technology stacks
  - Suggests appropriate roles
  - Allows manual role adjustment
  - Seeds demo tasks automatically
- 🧪 **Comprehensive Testing**: Stack detection test suite
  - Tests for all 10 supported stack clusters
  - Auto-configuration validation
  - Role template verification
- 📚 **Stack-Specific Examples**: Tailored task templates for each technology
  - Next.js: SSR, i18n, optimization tasks
  - Python: Async operations, ML deployment
  - Mobile: Biometric auth, offline sync
  - Go: gRPC, distributed tracing
  - Desktop: Auto-updates, native integrations

### Changed
- 🔧 **setup.py**: Smarter stack detection with subtype analysis
  - Reads package.json, requirements.txt, go.mod contents
  - Detects specific frameworks (React vs Vue, Django vs FastAPI)
  - Suggests optimal roles per detected stack
- 📝 **conductor-init.sh**: Enhanced onboarding experience
  - Shows detected stacks after setup
  - Interactive role configuration prompt
  - Demo task seeding
  - Optional agent startup
- 🎨 **README.md**: Updated with 90% coverage messaging
  - Stack support matrix
  - AI code review feature highlights
  - Enhanced value propositions

### Fixed
- 🐛 Glob pattern support for .NET project detection (*.csproj)
- 🔒 Code-reviewer role always included in auto-configuration
- 📋 Demo tasks only created if none exist

## [1.0.1] - 2024-07-22

### Added
- 🖥️ **Warp-Optimized Workflow**: Code Conductor now detects Warp and can open each agent's worktree in an AI-powered terminal on macOS, Linux, or Windows
- 📱 Cross-platform terminal support with fallbacks (iTerm2, Kitty, Alacritty, Windows Terminal)
- 🛠️ Enhanced `gtopen` and `gtwarp` commands in worktree helper
- 📊 Storage footprint guidance and cleanup recommendations

### Fixed
- 🔒 Atomic file writes with flush/fsync for better reliability
- 📝 Consistent `files_locked` schema across all scripts
- 🔄 Random agent ID collision prevention
- 🎯 Platform-specific terminal guidance (macOS vs Linux/Windows)

### Changed
- 📋 Updated documentation to clarify Conductor app is macOS-only
- 🔧 Improved bootstrap script with intelligent terminal detection

## [1.0.0] - 2024-07-22

### Added
- 🎼 Initial release of Code Conductor
- 🤖 Hybrid role system with default "dev" and specialized roles
- 📋 GitHub Issues integration with `conductor:task` labels
- 🔒 Conflict prevention via git worktrees and file locking
- 🔄 Self-healing system with automated health checks
- 🚀 Interactive setup script (`setup.py`) with stack detection
- 📊 Real-time monitoring and status reporting
- 🧹 Automated cleanup for stale work and completed tasks
- 📱 Support for Chrome Extension, React, Python microservices, and Tauri projects
- 🎯 Universal bootstrap script for agent initialization
- 📚 Comprehensive usage documentation for both GUI and terminal workflows
- ⚡ One-command installation via `install.sh`
- 🛠️ Advanced error handling and recovery mechanisms
- 🔍 Configuration validation and dependency checking
- 📦 Release automation with GitHub Actions

### Features
- **Agent Coordination**: Multi-agent task management with conflict prevention
- **GitHub Integration**: Native issue-to-task conversion with labels
- **Stack Detection**: Auto-configuration for popular development stacks
- **Dual Workflows**: Support for both Conductor desktop app and manual terminal usage
- **Health Monitoring**: Automated system health checks and reporting
- **Worktree Isolation**: Git worktree-based isolation for parallel work
- **Zero Config**: Automatic setup for 90% of GitHub-based projects

### Documentation
- Complete usage guide with examples for both workflows
- Installation and setup instructions
- Troubleshooting guide
- Contributing guidelines
- GitHub issue and PR templates

### Examples
- Chrome Extension + NextJS monorepo configuration
- React web application with modern tooling
- Python microservices with Docker support
- Tauri desktop application setup

## [Unreleased]
- Initial development and testing

---

**Legend:**
- 🎼 Core orchestration features
- 🤖 Agent management
- 📋 Task management
- 🔒 Conflict prevention
- 🔄 Automation
- 🚀 Setup and installation
- 📊 Monitoring and reporting
- 🧹 Cleanup and maintenance
- 📱 Project type support
- 🎯 User experience
- 📚 Documentation
- ⚡ Performance
- 🛠️ Developer experience
- 🔍 Validation and testing
- �� Release management 