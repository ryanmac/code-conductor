# Examples - Works with Your Stack

## React Web App - Modern full-stack development

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

## Chrome Extension + NextJS - Browser extension with web dashboard

```yaml
project_name: symphony-extension
roles:
  default: dev
  specialized: [devops]
protected_files:
  - packages/extension/manifest.json
```

## Python Microservices - Scalable backend architecture

```yaml
project_name: api-platform
roles:
  default: dev
  specialized: [devops, security]
quality_checks:
  - pytest --cov=services
  - bandit -r services/
```

## Tauri Desktop App - Cross-platform Rust + JS application

```yaml
project_name: desktop-app
roles:
  default: dev
  specialized: [devops, security, rust-dev]
matrix_builds: [ubuntu, macos, windows]
```

**Don't see your stack?** [Contribute an example](../CONTRIBUTING.md) and help other developers!