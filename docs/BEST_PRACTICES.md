# Best Practices

1. **Task Design**: Make tasks self-contained with clear specs
2. **Duplicate Prevention**: Check existing issues before creating new ones - use `./conductor check-dup "title"`
3. **Role Selection**: Start with dev-only, add specializations as needed
4. **Regular Cleanup**: Let automation handle stale work
5. **Monitor Health**: Check status issue regularly
6. **Incremental Adoption**: Start small, expand as comfortable

See also: [Duplicate Prevention Guide](DUPLICATE_PREVENTION.md) for detailed strategies

## Task Format

Tasks are created as GitHub Issues with complete specifications:

**Issue Title**: Implement authentication

**Issue Body**:
```markdown
## Description
Implement user authentication system for the application.

## Specifications
See: docs/auth-spec.md

## Best Practices
- Use JWT tokens
- Implement refresh tokens

## Success Criteria
- Tests: 100% coverage
- Security: Pass security scan
```

**Labels**:
- `conductor:task` (required)
- `effort:medium`
- `priority:medium`
- `skill:backend` (optional, for specialized tasks)