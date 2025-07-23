# Code Conductor Development Makefile

.PHONY: help install demo validate clean test setup

# Default target
help: ## Show this help message
	@echo "🎼 Code Conductor Development Commands"
	@echo "======================================"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Install code-conductor in current directory
	@echo "🚀 Installing Code Conductor..."
	@bash install.sh --auto

demo: ## Create and run a full demo
	@echo "🎬 Creating Code Conductor Demo..."
	@echo "=================================="
	@echo ""
	@echo "📁 Setting up demo environment..."
	@mkdir -p /tmp/conductor-demo
	@cd /tmp/conductor-demo && git init
	@cd /tmp/conductor-demo && git config user.name "Demo User"
	@cd /tmp/conductor-demo && git config user.email "demo@example.com"
	@cd /tmp/conductor-demo && echo "# Demo Project" > README.md
	@cd /tmp/conductor-demo && git add README.md
	@cd /tmp/conductor-demo && git commit -m "Initial commit"
	@echo "✅ Demo repository created"
	@echo ""
	@echo "🎼 Installing code-conductor..."
	@cd /tmp/conductor-demo && cp -r $(PWD)/.conductor .
	@cd /tmp/conductor-demo && cp -r $(PWD)/examples .conductor/
	@cd /tmp/conductor-demo && cp $(PWD)/setup.py .
	@cd /tmp/conductor-demo && cp $(PWD)/.gitignore .conductor-gitignore
	@cd /tmp/conductor-demo && cat .conductor-gitignore >> .gitignore || cp .conductor-gitignore .gitignore
	@echo "✅ Files copied"
	@echo ""
	@echo "⚙️  Running auto setup..."
	@cd /tmp/conductor-demo && python setup.py --auto
	@echo "✅ Setup complete"
	@echo ""
	@echo "📋 Creating demo task..."
	@echo "⚠️  Note: Demo tasks require GitHub CLI authentication."
	@echo "   Run 'gh auth login' if not authenticated."
	@echo "   Tasks will be created as GitHub Issues when you run bootstrap.sh"
	@echo "✅ Demo environment ready"
	@echo ""
	@echo "🎯 Demo is ready!"
	@echo "=================="
	@echo "Demo location: /tmp/conductor-demo"
	@echo ""
	@echo "Try these commands:"
	@echo "  cd /tmp/conductor-demo"
	@echo "  bash .conductor/scripts/bootstrap.sh dev"
	@echo "  python .conductor/scripts/health-check.py"
	@echo "  python .conductor/scripts/update-status.py"
	@echo ""
	@echo "🧹 To clean up: rm -rf /tmp/conductor-demo"

validate: ## Validate the code-conductor configuration
	@echo "🔍 Validating Code Conductor..."
	@python .conductor/scripts/validate-config.py

test: ## Run all system tests
	@echo "🧪 Running Code Conductor Tests..."
	@echo "=================================="
	@echo ""
	@echo "🔐 GitHub CLI check..."
	@if command -v gh >/dev/null 2>&1; then \
		if gh auth status >/dev/null 2>&1; then \
			echo "✅ GitHub CLI authenticated"; \
		else \
			echo "⚠️  GitHub CLI not authenticated. Some tests may fail."; \
		fi; \
	else \
		echo "⚠️  GitHub CLI not installed. Some tests will be skipped."; \
	fi
	@echo ""
	@echo "📋 Configuration validation..."
	@python .conductor/scripts/validate-config.py --strict
	@echo "✅ Configuration valid"
	@echo ""
	@echo "🔍 Dependency check..."
	@python .conductor/scripts/dependency-check.py
	@echo "✅ Dependencies satisfied"
	@echo ""
	@echo "🎯 Testing bootstrap script..."
	@bash -n .conductor/scripts/bootstrap.sh
	@echo "✅ Bootstrap script syntax valid"
	@echo ""
	@if command -v gh >/dev/null 2>&1 && gh auth status >/dev/null 2>&1; then \
		echo "📊 Health check test..."; \
		GITHUB_TOKEN=$$(gh auth token) python .conductor/scripts/health-check.py; \
		echo "✅ Health check working"; \
	else \
		echo "⏩ Skipping health check (requires GitHub CLI)"; \
	fi
	@echo ""
	@echo "🎉 All tests passed!"

setup: ## Interactive setup for development
	@echo "🔧 Code Conductor Development Setup"
	@echo "===================================="
	@python setup.py

clean: ## Clean up generated files and caches
	@echo "🧹 Cleaning up..."
	@find . -name "*.pyc" -delete
	@find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
	@rm -rf dist/
	@rm -rf *.egg-info/
	@rm -rf .pytest_cache/
	@rm -rf worktrees/
	@echo "✅ Cleanup complete"

quick-start: ## Show quick start instructions
	@echo "🎼 Code Conductor Quick Start"
	@echo "============================="
	@echo ""
	@echo "1. Install in your project:"
	@echo "   bash <(curl -fsSL https://raw.githubusercontent.com/ryanmac/code-conductor/main/conductor-init.sh)"
	@echo ""
	@echo "2. Authenticate GitHub CLI (if not already done):"
	@echo "   gh auth login"
	@echo ""
	@echo "3. Create a task via GitHub issue:"
	@echo "   gh issue create --label 'conductor:task' --title 'Your task'"
	@echo ""
	@echo "4. Launch an agent:"
	@echo "   bash .conductor/scripts/bootstrap.sh dev"
	@echo ""
	@echo "4. Open workspace in Conductor app (follow bootstrap instructions)"
	@echo ""
	@echo "📚 Full guide: docs/USAGE.md"

dev-aliases: ## Install helpful development aliases
	@echo "🛠️  Installing development aliases..."
	@echo "# Code Conductor Development Aliases" >> ~/.bashrc
	@echo "alias ctr='cd worktrees && ls'" >> ~/.bashrc
	@echo "alias cth='python .conductor/scripts/health-check.py'" >> ~/.bashrc
	@echo "alias cts='python .conductor/scripts/update-status.py'" >> ~/.bashrc
	@echo "alias ctc='python .conductor/scripts/cleanup-stale.py'" >> ~/.bashrc
	@echo "alias ctv='python .conductor/scripts/validate-config.py'" >> ~/.bashrc
	@echo "✅ Aliases added to ~/.bashrc"
	@echo "Run 'source ~/.bashrc' to load them"

version: ## Show version information
	@echo "🎼 Code Conductor v$$(cat VERSION)"
	@echo "📅 Release: $$(head -1 CHANGELOG.md | grep -o '\[.*\]' | tr -d '[]')" 