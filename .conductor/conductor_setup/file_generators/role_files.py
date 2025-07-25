"""
Role Files Generator
Generates role definition markdown files
"""

from pathlib import Path
from typing import Dict, Any


class RoleFileGenerator:
    """Generates role definition files for AI agents"""

    def __init__(self, project_root: Path, config: Dict[str, Any]):
        self.project_root = project_root
        self.conductor_dir = project_root / ".conductor"
        self.config = config

    def create_role_definitions(self):
        """Create role definition files"""
        print("\n📄 Creating role definitions...")

        roles_dir = self.conductor_dir / "roles"
        roles_dir.mkdir(exist_ok=True)

        # Always create the default dev role
        self._create_dev_role(roles_dir)

        # Create specialized roles
        for role in self.config["roles"]["specialized"]:
            self._create_specialized_role(roles_dir, role)

    def _create_dev_role(self, roles_dir: Path):
        """Create the default dev role file"""
        dev_content = """# Dev Role (Default Generalist)

## Overview
The dev role is the default generalist role that can work on any task without
specific skill requirements. This role embodies the "super dev" concept where
well-documented tasks enable any developer to contribute effectively.

## Responsibilities
- Implement features according to task specifications
- Write tests to meet coverage requirements
- Follow project coding standards and best practices
- Create pull requests with clear descriptions
- Update documentation as needed

## Task Selection Criteria
- Can claim any task without specific skill requirements
- Prioritizes tasks marked as 'ready' with no blockers
- Avoids tasks that explicitly require specialized roles

## Best Practices
1. Always read the complete task specification before starting
2. Check for existing implementations or patterns in the codebase
3. Run tests locally before pushing changes
4. Use meaningful commit messages
5. Ask questions via GitHub issues if specifications are unclear

## Success Metrics
- All tests passing
- Code coverage maintained or improved
- No security vulnerabilities introduced
- PR approved and merged
"""

        dev_file = roles_dir / "dev.md"
        with open(dev_file, "w") as f:
            f.write(dev_content)
        print(f"✓ Created {dev_file}")

    def _create_specialized_role(self, roles_dir: Path, role: str):
        """Create a specialized role file"""
        role_templates = self._get_role_templates()

        if role in role_templates:
            role_file = roles_dir / f"{role}.md"
            with open(role_file, "w") as f:
                f.write(role_templates[role])
            print(f"✓ Created {role_file}")
        else:
            # Create a basic template for custom roles
            custom_content = f"""# {role.title()} Role

## Overview
Custom role for {role} responsibilities.

## Responsibilities
- [Add specific responsibilities]

## Task Selection Criteria
- Tasks labeled with '{role}'
- [Add specific criteria]

## Required Skills
- [Add required skills]

## Success Metrics
- [Add success metrics]
"""
            role_file = roles_dir / f"{role}.md"
            with open(role_file, "w") as f:
                f.write(custom_content)
            print(f"✓ Created {role_file} (custom template)")

    def _get_role_templates(self) -> Dict[str, str]:
        """Get predefined role templates"""
        return {
            "devops": """# DevOps Role

## Overview
The DevOps role handles CI/CD, infrastructure, deployments, and system reliability.

## Responsibilities
- Maintain and improve CI/CD pipelines
- Manage deployment configurations
- Monitor system health and performance
- Implement infrastructure as code
- Ensure security best practices in deployments

## Task Selection Criteria
- Tasks labeled with 'devops' or 'infrastructure'
- Deployment and release-related tasks
- Performance optimization tasks
- Monitoring and alerting setup

## Required Skills
- GitHub Actions or similar CI/CD tools
- Container orchestration (Docker, Kubernetes)
- Cloud platforms (AWS, GCP, Azure)
- Infrastructure as Code (Terraform, CloudFormation)

## Success Metrics
- CI/CD pipeline success rate > 95%
- Deployment rollback capability verified
- Infrastructure changes documented
- Security scans passing
""",
            "security": """# Security Role

## Overview
The Security role focuses on application security, vulnerability management,
and compliance.

## Responsibilities
- Conduct security audits and reviews
- Implement security best practices
- Manage dependency vulnerabilities
- Ensure compliance with security policies
- Educate team on security practices

## Task Selection Criteria
- Tasks labeled with 'security' or 'vulnerability'
- Authentication and authorization implementations
- Dependency update tasks with security implications
- Compliance and audit-related tasks

## Required Skills
- OWASP Top 10 knowledge
- Security scanning tools (npm audit, Snyk, etc.)
- Authentication protocols (OAuth, JWT)
- Encryption and key management

## Success Metrics
- Zero high/critical vulnerabilities
- Security tests implemented and passing
- Compliance requirements documented
- Security review completed and approved
""",
            "ml-engineer": """# ML Engineer Role

## Overview
The ML Engineer role handles machine learning models, data pipelines, and AI
integrations.

## Responsibilities
- Develop and train ML models
- Implement data preprocessing pipelines
- Integrate ML models into applications
- Monitor model performance and drift
- Document model architectures and datasets

## Task Selection Criteria
- Tasks labeled with 'ml' or 'ai'
- Data pipeline implementations
- Model training and evaluation tasks
- Performance optimization for ML workloads

## Required Skills
- Python ML frameworks (TensorFlow, PyTorch, scikit-learn)
- Data processing tools (Pandas, NumPy)
- MLOps practices and tools
- Model evaluation and metrics

## Success Metrics
- Model performance meets specified thresholds
- Data pipelines tested and documented
- Model versioning implemented
- Performance benchmarks documented
""",
            "ui-designer": """# UI Designer Role

## Overview
The UI Designer role focuses on user interface, design systems, and user experience.

## Responsibilities
- Implement design systems and components
- Ensure UI consistency across the application
- Optimize for accessibility (a11y)
- Implement responsive designs
- Collaborate on UX improvements

## Task Selection Criteria
- Tasks labeled with 'ui', 'design', or 'frontend'
- Component library implementations
- Accessibility improvements
- Design system updates

## Required Skills
- Modern CSS and styling approaches
- Component libraries (React, Vue, etc.)
- Accessibility standards (WCAG)
- Design tools integration

## Success Metrics
- Accessibility score > 95
- Component reusability achieved
- Design consistency maintained
- Performance metrics met (LCP, FID, CLS)
""",
            "code-reviewer": """# Code Reviewer Role (AI-Powered)

## Overview
The Code Reviewer role provides automated AI-powered code reviews on pull
requests, similar to CodeRabbit. This role runs automatically on all PRs to
ensure code quality, catch bugs, and suggest improvements.

## Responsibilities
- Review all pull requests automatically
- Identify potential bugs and security issues
- Suggest code improvements and optimizations
- Ensure coding standards compliance
- Check for test coverage
- Identify breaking changes
- Suggest documentation updates

## Task Selection Criteria
- Automatically triggered on PR creation/update
- Reviews all code changes
- Provides feedback as PR comments
- Can be manually invoked for specific reviews

## Review Focus Areas
- Code quality and maintainability
- Security vulnerabilities
- Performance issues
- Test coverage gaps
- Documentation completeness
- Breaking API changes
- Best practices adherence

## Success Metrics
- Average review time < 5 minutes
- False positive rate < 10%
- Developer satisfaction score > 4/5
- Bugs caught before merge
""",
            "frontend": """# Frontend Developer Role

## Overview
The Frontend role specializes in client-side development, UI implementation,
and user experience.

## Responsibilities
- Implement responsive UI components
- Optimize frontend performance
- Ensure cross-browser compatibility
- Implement state management
- Create reusable component libraries

## Task Selection Criteria
- Tasks labeled with 'frontend', 'ui', or 'client'
- Component development tasks
- Frontend optimization tasks
- UI/UX implementation tasks

## Required Skills
- Modern JavaScript/TypeScript
- Frontend frameworks (React, Vue, Angular, Svelte)
- CSS/SASS and modern styling
- Build tools (Webpack, Vite, etc.)
- Performance optimization

## Success Metrics
- Lighthouse scores > 90
- Component test coverage > 80%
- Zero accessibility violations
- Bundle size optimized
""",
            "mobile": """# Mobile Developer Role

## Overview
The Mobile role specializes in mobile application development across platforms.

## Responsibilities
- Develop mobile applications
- Ensure platform-specific optimizations
- Implement native features
- Optimize for mobile performance
- Handle offline functionality

## Task Selection Criteria
- Tasks labeled with 'mobile', 'ios', or 'android'
- Mobile-specific feature implementations
- Platform optimization tasks
- Mobile UI/UX tasks

## Required Skills
- React Native / Flutter / Native development
- Mobile platform guidelines (iOS/Android)
- Mobile performance optimization
- Push notifications and device APIs
- App store deployment

## Success Metrics
- App performance metrics met
- Crash-free rate > 99%
- App store rating > 4.5
- Platform compliance achieved
""",
            "data": """# Data Engineer Role

## Overview
The Data Engineer role focuses on data pipelines, analytics, and data infrastructure.

## Responsibilities
- Build and maintain data pipelines
- Implement data transformations
- Ensure data quality and integrity
- Optimize data storage and retrieval
- Create data visualization solutions

## Task Selection Criteria
- Tasks labeled with 'data', 'etl', or 'analytics'
- Data pipeline implementations
- Database optimization tasks
- Analytics and reporting tasks

## Required Skills
- SQL and NoSQL databases
- Data processing frameworks
- ETL/ELT tools
- Data visualization tools
- Big data technologies

## Success Metrics
- Pipeline reliability > 99%
- Data quality scores met
- Query performance optimized
- Documentation complete
""",
        }
