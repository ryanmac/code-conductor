# Core Agentic Charter

## Agentic Workflow Loop (ReAct Pattern)

Every Conductor-Score agent follows this core reasoning and acting pattern:

### 1. 🔍 **Observe**
- Read task specification and success criteria
- Check repository state (`git status`, recent commits)
- Review CI/CD status (`gh run list --limit 5`)
- Scan relevant files and documentation
- Understand the project's technology stack

### 2. 🧠 **Plan**
- Break down the task into subtasks
- Identify files that need modification
- List required tools and dependencies
- Define evaluation methods (tests, linters, etc.)
- Consider potential risks and edge cases
- Set a token budget for complex reasoning

### 3. 🛠️ **Act**
- Execute the smallest safe step
- Commit changes with clear messages
- Run local validation before pushing
- Use atomic operations when possible
- Document decisions in code comments

### 4. ✅ **Evaluate**
- Run relevant tests (`npm test`, `pytest`, etc.)
- Check linter output (`black`, `eslint`, etc.)
- Verify success criteria are met
- Compare results to expectations
- Monitor resource usage and performance

### 5. 🔄 **Reflect**
- Analyze any failures or unexpected results
- Adjust approach based on feedback
- Consider alternative solutions
- Learn from patterns for future tasks

### 6. 📝 **Record**
- Update task status in workflow-state.json
- Document key decisions and rationale
- Log any blockers or dependencies
- Prepare handoff notes for other agents
- Update PR description with progress

## Token Budget Management

### Standard Budgets
- **Quick tasks**: 4K tokens
- **Standard tasks**: 8K tokens  
- **Complex tasks**: 16K tokens
- **Ultrathink mode**: 32K tokens (requires escalation)

### When to Escalate
- Architecture decisions affecting multiple systems
- Security-critical implementations
- Breaking changes to public APIs
- Performance optimizations with unclear trade-offs

## Quality Gates

All agents must ensure:

### Code Quality
- ✅ All tests pass (`CI: green`)
- ✅ Coverage maintained or improved (target: ≥85%)
- ✅ Zero critical linter errors
- ✅ No security vulnerabilities introduced
- ✅ Performance benchmarks pass (if applicable)

### Documentation
- ✅ Code comments for complex logic
- ✅ API documentation updated
- ✅ README reflects any new features
- ✅ CHANGELOG entry for user-facing changes

### Collaboration
- ✅ Clear commit messages following conventional commits
- ✅ PR description explains the "why"
- ✅ Handoff notes for next agent
- ✅ Review requested from appropriate specialists

## Error Recovery

When blocked:
1. **Document the blocker** with specific error messages
2. **Attempt standard fixes** (cache clear, dependency update)
3. **Search for similar issues** in GitHub Issues/Discussions
4. **Escalate to specialist** if domain-specific
5. **Mark task as blocked** with clear next steps

## Context Management

### Before Starting
```bash
# Refresh your understanding
git pull origin main
gh pr list --state open
cat .conductor/workflow-state.json | jq '.active_work'
```

### During Work
```bash
# Maintain clean state
git status
git diff --staged
npm test -- --watch  # or equivalent
```

### Before Handoff
```bash
# Ensure reproducibility
git push origin $(git branch --show-current)
echo "## Handoff Notes" >> .conductor/handoff.md
```

## Cross-Role Communication

### Standard Handoff Protocol
1. **Update task status** with completion percentage
2. **Write handoff notes** including:
   - What was completed
   - What remains
   - Any discovered issues
   - Suggested next steps
3. **Tag relevant specialist** in PR comment
4. **Update workflow-state.json** with agent transition

### Escalation Triggers
- 🔒 Security implications → `@security`
- 🚀 Deployment changes → `@devops`
- 🎨 UI/UX concerns → `@ui-designer`
- 📊 Data integrity → `@data`
- 🤖 ML model changes → `@ml-engineer`

## Success Metrics

Track and report:
- **Task completion time** vs. estimate
- **Code quality scores** (coverage, complexity)
- **Review turnaround time**
- **Production incident rate** post-deployment
- **Developer satisfaction** (PR feedback)

---

*Remember: You are part of an orchestrated team. Quality over speed, clarity over cleverness, and collaboration over isolation.*