# CLAUDE.md: Instructions for Claude Code - Agent Roles

## Purpose
This directory contains agent role definitions for the Conductor-Score orchestration system. Each `.md` file defines a specific agent type (dev, devops, security, etc.) with responsibilities, skills, and workflows. Claude Code should use these definitions to understand agent capabilities and generate compatible extensions without disrupting the orchestration system.

## Guidelines
- **Do**: Always reference `_core.md` for the base agentic workflow (ReAct pattern)
- **Do**: Inherit patterns from existing roles when creating new ones
- **Do**: Respect the contracts defined in `../contracts.md` for inter-role communication
- **Don't**: Modify original role files directly - create new files for custom roles
- **Don't**: Break the hybrid model (generalist `dev` + specialists) without clear justification
- **Don't**: Generate roles that bypass security or quality checks

## Autonomous Decision Tree for Role Operations

### When to Use Existing Roles vs. Create New Ones

```
Task requires role assignment?
├─ YES: Check required_skills in task
│   ├─ Empty [] → Use 'dev' role (generalist)
│   ├─ Contains ["frontend"] → Use 'frontend' role
│   ├─ Contains ["devops"] → Use 'devops' role
│   ├─ Contains ["security"] → Use 'security' role
│   └─ Contains unknown skill → Check if partial match exists
│       ├─ 70%+ match → Use closest role
│       └─ <70% match → Create new role following patterns
└─ NO: Default to 'dev' role
```

### When to Create a New Role

```
New skill requirement detected?
├─ Check overlap with existing roles
│   ├─ >50% overlap → Extend existing role instead
│   └─ <50% overlap → Create new role
├─ Validate need
│   ├─ Used in 3+ tasks → Definitely create
│   ├─ Used in 1-2 tasks → Consider if 'dev' can handle
│   └─ Highly specialized → Create if clear domain boundary
└─ Create following _core.md patterns
```

## Step-by-Step Usage

### 1. Observe - Understanding Existing Roles
Automatically read and analyze:
- **Structure**: Each role has sections for Overview, Responsibilities, Skills, Task Selection, etc.
- **Patterns**: Notice how specialized roles build on the `_core.md` foundation
- **Contracts**: Check `../contracts.md` for how roles interact

### 2. Plan - Think Through Extensions
Automated checks:
- Gap analysis against current task requirements
- Role overlap calculation
- Contract compatibility verification
- Boundary definition based on existing patterns

### 3. Act - Generate Role Definitions
When creating new roles:
```markdown
# custom-roles/[role-name].md

# [Role Name] Agent

## Overview
[Clear purpose statement inheriting from _core.md patterns]

## Core Responsibilities
[Specific tasks this role handles that others don't]

## Required Skills
[Technical competencies needed]

## Task Selection Criteria
[How this agent decides which tasks to claim]

## Workflow Patterns
[Specific ReAct adaptations for this domain]

## Quality Standards
[Acceptance criteria specific to this role]

## Collaboration Contracts
[Reference to ../contracts.md entries or new contracts]
```

### 4. Evaluate - Test Role Compatibility
Verify new roles by:
- Checking they don't duplicate existing capabilities
- Ensuring they follow the ReAct pattern from `_core.md`
- Validating contract interfaces if adding new interactions
- Testing with sample task assignments

## Examples

### Example 1: Extending for a New Domain
**Scenario**: Task requires database optimization skills not in existing roles

**Autonomous approach**:
```python
# Decision logic
if "database-optimization" in task.required_skills:
    existing_match = find_best_role_match("database-optimization")
    if existing_match.score < 0.7:
        # Auto-generate new role
        create_role_from_template("db-optimizer", {
            "base": "dev.md",
            "additions": ["query optimization", "indexing", "migrations"],
            "evaluation": ["query performance tests", "index usage analysis"]
        })
```

### Example 2: Creating Domain-Specific Variant
**Prompt**: "Create a frontend-react specialist variant of frontend.md for React-specific projects"

**Expected approach**:
1. Read frontend.md for base UI/UX patterns
2. Add React-specific skills (hooks, state management, component patterns)
3. Include React-specific quality checks (prop-types, React Testing Library)
4. Maintain compatibility with existing contracts

### Example 3: Role for New Stack
**Prompt**: "Generate a role for Rust backend development based on dev.md patterns"

**Expected approach**:
1. Inherit general development workflow from dev.md
2. Add Rust-specific sections:
   - Memory safety considerations
   - Cargo-specific commands
   - Performance benchmarking steps
3. Keep contract interfaces compatible

## Warnings
- **State Conflicts**: Never generate roles that directly modify `workflow-state.json` outside of proper task claiming
- **Security**: Avoid roles that bypass code review or security scanning steps
- **Isolation**: Ensure roles respect worktree isolation (one agent per worktree)
- **Performance**: Consider token budget management (see _core.md section on this)
- **Contracts**: Breaking existing contracts in `../contracts.md` will disrupt multi-agent collaboration

## Best Practices
1. **Modularity**: Create roles that do one thing well rather than everything poorly
2. **Inheritance**: Always build on `_core.md` patterns rather than starting from scratch
3. **Documentation**: Include clear examples in your generated roles
4. **Testing**: Provide sample tasks that demonstrate when to use the new role
5. **Compatibility**: Ensure new roles work with existing GitHub Actions workflows

## References
- `_core.md` - Base agentic workflow all roles must follow
- `../contracts.md` - Inter-role communication contracts
- `../config.yaml` - Project configuration including active roles
- `dev.md` - Default generalist role (good starting template)
- `code-reviewer.md` - Example of specialized automated role

Last Updated: 2025-07-23
Version: 1.0