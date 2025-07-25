"""
Express configuration presets for common project types
"""

from typing import Dict, Any, Optional

# Express configurations for common project types
EXPRESS_CONFIGS = {
    "react-typescript": {
        "patterns": ["react", "typescript", "tsx", "jsx"],
        "roles": {"default": "dev", "specialized": ["frontend", "code-reviewer"]},
        "github_integration": {"issue_to_task": True, "pr_reviews": True},
        "build_validation": ["npm test", "npm run build"],
        "suggested_tasks": [
            {
                "title": "Set up component testing with React Testing Library",
                "labels": ["conductor:task", "testing", "frontend"],
            },
            {
                "title": "Add Storybook for component development",
                "labels": ["conductor:task", "enhancement", "frontend"],
            },
            {
                "title": "Configure ESLint and Prettier",
                "labels": ["conductor:task", "code-quality", "dev-experience"],
            },
        ],
    },
    "python-fastapi": {
        "patterns": ["fastapi", "python", "uvicorn", "pydantic"],
        "roles": {"default": "dev", "specialized": ["backend", "code-reviewer"]},
        "github_integration": {"issue_to_task": True, "pr_reviews": True},
        "build_validation": ["pytest", "black --check ."],
        "suggested_tasks": [
            {
                "title": "Add API documentation with OpenAPI",
                "labels": ["conductor:task", "documentation", "backend"],
            },
            {
                "title": "Set up database migrations with Alembic",
                "labels": ["conductor:task", "database", "backend"],
            },
            {
                "title": "Add integration tests for endpoints",
                "labels": ["conductor:task", "testing", "backend"],
            },
        ],
    },
    "nextjs-fullstack": {
        "patterns": ["next", "react", "vercel"],
        "roles": {
            "default": "dev",
            "specialized": ["frontend", "backend", "code-reviewer"],
        },
        "github_integration": {"issue_to_task": True, "pr_reviews": True},
        "build_validation": ["npm test", "npm run build", "npm run lint"],
        "suggested_tasks": [
            {
                "title": "Set up authentication with NextAuth.js",
                "labels": ["conductor:task", "auth", "fullstack"],
            },
            {
                "title": "Configure Prisma for database access",
                "labels": ["conductor:task", "database", "backend"],
            },
            {
                "title": "Add E2E tests with Playwright",
                "labels": ["conductor:task", "testing", "e2e"],
            },
        ],
    },
    "vue-javascript": {
        "patterns": ["vue", "nuxt", "vite"],
        "roles": {"default": "dev", "specialized": ["frontend", "code-reviewer"]},
        "github_integration": {"issue_to_task": True, "pr_reviews": True},
        "build_validation": ["npm test", "npm run build"],
        "suggested_tasks": [
            {
                "title": "Set up Pinia for state management",
                "labels": ["conductor:task", "state-management", "frontend"],
            },
            {
                "title": "Add component testing with Vitest",
                "labels": ["conductor:task", "testing", "frontend"],
            },
            {
                "title": "Configure Vue Router for navigation",
                "labels": ["conductor:task", "routing", "frontend"],
            },
        ],
    },
    "python-django": {
        "patterns": ["django", "python", "wsgi"],
        "roles": {"default": "dev", "specialized": ["backend", "code-reviewer"]},
        "github_integration": {"issue_to_task": True, "pr_reviews": True},
        "build_validation": ["python manage.py test", "black --check ."],
        "suggested_tasks": [
            {
                "title": "Set up Django REST framework",
                "labels": ["conductor:task", "api", "backend"],
            },
            {
                "title": "Configure Celery for async tasks",
                "labels": ["conductor:task", "async", "backend"],
            },
            {
                "title": "Add Django Debug Toolbar",
                "labels": ["conductor:task", "dev-experience", "backend"],
            },
        ],
    },
    "go-microservices": {
        "patterns": ["go", "gin", "fiber", "echo"],
        "roles": {"default": "dev", "specialized": ["backend", "code-reviewer"]},
        "github_integration": {"issue_to_task": True, "pr_reviews": True},
        "build_validation": ["go test ./...", "go build"],
        "suggested_tasks": [
            {
                "title": "Set up structured logging with zerolog",
                "labels": ["conductor:task", "observability", "backend"],
            },
            {
                "title": "Add OpenTelemetry instrumentation",
                "labels": ["conductor:task", "observability", "backend"],
            },
            {
                "title": "Create Dockerfile and docker-compose",
                "labels": ["conductor:task", "devops", "containers"],
            },
        ],
    },
    "rust-cli": {
        "patterns": ["rust", "cargo", "clap"],
        "roles": {"default": "dev", "specialized": ["backend", "code-reviewer"]},
        "github_integration": {"issue_to_task": True, "pr_reviews": True},
        "build_validation": ["cargo test", "cargo build --release"],
        "suggested_tasks": [
            {
                "title": "Add comprehensive CLI tests",
                "labels": ["conductor:task", "testing", "cli"],
            },
            {
                "title": "Set up GitHub release workflow",
                "labels": ["conductor:task", "ci-cd", "devops"],
            },
            {
                "title": "Add shell completion generation",
                "labels": ["conductor:task", "enhancement", "cli"],
            },
        ],
    },
    "mobile-react-native": {
        "patterns": ["react-native", "expo", "ios", "android"],
        "roles": {"default": "dev", "specialized": ["mobile", "code-reviewer"]},
        "github_integration": {"issue_to_task": True, "pr_reviews": True},
        "build_validation": ["npm test", "npm run lint"],
        "suggested_tasks": [
            {
                "title": "Set up Detox for E2E testing",
                "labels": ["conductor:task", "testing", "mobile"],
            },
            {
                "title": "Configure push notifications",
                "labels": ["conductor:task", "feature", "mobile"],
            },
            {
                "title": "Add crash reporting with Sentry",
                "labels": ["conductor:task", "monitoring", "mobile"],
            },
        ],
    },
}


def get_express_config(stack_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Match detected stack to express config"""
    # Use the primary stack from summary if available
    if stack_info.get("summary", {}).get("primary_stack"):
        stack_name = stack_info["summary"]["primary_stack"]
        if stack_name in EXPRESS_CONFIGS:
            return EXPRESS_CONFIGS[stack_name]

    # Otherwise try pattern matching
    detected_items = set()
    detected_items.update(stack_info.get("frameworks", []))
    detected_items.update(stack_info.get("summary", {}).get("languages", []))
    detected_items.update(stack_info.get("summary", {}).get("tools", []))

    # Add items from modern tools
    modern = stack_info.get("modern_tools", {})
    if modern.get("framework"):
        detected_items.add(modern["framework"])
    if modern.get("build_tool"):
        detected_items.add(modern["build_tool"])

    # Find best match
    best_match = None
    best_score = 0

    for stack_name, config in EXPRESS_CONFIGS.items():
        score = len(detected_items.intersection(config["patterns"]))
        if score > best_score:
            best_match = stack_name
            best_score = score

    return EXPRESS_CONFIGS.get(best_match) if best_match and best_score > 0 else None
