# Changelog

All notable changes to Conductor-Score will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.1] - 2024-07-22

### Added
- 🖥️ **Warp-Optimized Workflow**: Conductor-Score now detects Warp and can open each agent's worktree in an AI-powered terminal on macOS, Linux, or Windows
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
- 🎼 Initial release of Conductor-Score
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