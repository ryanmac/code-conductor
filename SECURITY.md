# Security Policy

## Supported Versions

Use this section to tell people about which versions of your project are currently being supported with security updates.

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Reporting a Vulnerability

We take security vulnerabilities seriously. If you discover a security vulnerability in Conductor-Score, please follow these steps:

### 1. **DO NOT** create a public GitHub issue
Security vulnerabilities should be reported privately to prevent potential exploitation.

### 2. Email the maintainer
Send an email to the maintainer with the following information:
- **Subject:** `[SECURITY] Conductor-Score Vulnerability Report`
- **Description:** Detailed description of the vulnerability
- **Steps to reproduce:** Clear steps to reproduce the issue
- **Impact:** Potential impact of the vulnerability
- **Suggested fix:** If you have a suggested fix (optional)

### 3. Response timeline
- **Initial response:** Within 48 hours
- **Status update:** Within 1 week
- **Fix timeline:** Depends on severity and complexity

### 4. Disclosure
- Security vulnerabilities will be disclosed via GitHub Security Advisories
- Patches will be released as soon as possible
- Credit will be given to reporters in the advisory

## Security Best Practices

When using Conductor-Score:

1. **Keep dependencies updated:** Regularly update your dependencies to get security patches
2. **Review configurations:** Ensure your `.conductor/config.yaml` doesn't expose sensitive information
3. **Use virtual environments:** Always use virtual environments to isolate dependencies
4. **Monitor logs:** Check `.conductor/logs/` for any suspicious activity
5. **Secure your GitHub tokens:** If using GitHub integration, ensure tokens have minimal required permissions

## Dependencies

We regularly audit our dependencies for security vulnerabilities:

- **PyYAML:** Used for configuration parsing
- **Requests:** Used for HTTP operations
- **Standard library modules:** Python built-in modules

## Contact

For security issues, contact: ryan@updoot.co

For general support, use GitHub Issues. 