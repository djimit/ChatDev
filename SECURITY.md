# Security Policy

## Supported Versions

We release patches for security vulnerabilities for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

We take the security of ChatDev seriously. If you believe you have found a security vulnerability, please report it to us as described below.

### Please DO NOT:

- Open a public GitHub issue for security vulnerabilities
- Disclose the vulnerability publicly before it has been addressed

### Please DO:

1. **Email us directly** at [contact@camel-ai.org](mailto:contact@camel-ai.org) with:
   - A description of the vulnerability
   - Steps to reproduce the issue
   - Potential impact of the vulnerability
   - Any suggested fixes (if applicable)

2. **Allow time for response**: We will acknowledge your email within 48 hours and aim to provide a more detailed response within 7 days.

3. **Provide a reasonable amount of time** for us to address the issue before any disclosure to the public or a third party.

## Security Best Practices

When using ChatDev, please follow these security best practices:

### API Key Management

- **Never commit API keys** to version control
- Use environment variables or `.env` files (which should be in `.gitignore`)
- Rotate API keys regularly
- Use separate API keys for development, testing, and production
- Monitor API key usage for suspicious activity

### Input Validation

- **Sanitize all user inputs** before processing
- Validate project names and file paths to prevent directory traversal attacks
- Be cautious when using user-provided data in prompts

### File System Security

- **Restrict file system access** to designated directories (WareHouse)
- Do not execute generated code in production without thorough review
- Be aware that AI-generated code may contain security vulnerabilities

### Network Security

- **Use HTTPS** for all API communications
- Implement rate limiting to prevent API abuse
- Monitor network traffic for anomalies

### Code Review

- **Review all AI-generated code** before deployment
- Run security scans (bandit, safety) on generated projects
- Test generated applications in isolated environments first

### Dependency Management

- **Keep dependencies up to date** to patch known vulnerabilities
- Regularly run `safety check` to identify insecure packages
- Review dependency updates for breaking changes

## Known Security Considerations

### AI-Generated Code

ChatDev uses Large Language Models to generate code automatically. Please be aware:

1. **Code Quality Varies**: AI-generated code may contain:
   - Security vulnerabilities (SQL injection, XSS, etc.)
   - Logic errors
   - Insecure dependencies

2. **Prompt Injection**: Carefully validate and sanitize user-provided task prompts

3. **Data Privacy**: Do not include sensitive information in prompts as they are sent to OpenAI's API

### Command Execution

- Version 1.0.0+ includes fixes for command injection vulnerabilities
- Always use the latest version
- Git operations are now executed safely using subprocess with argument lists

### Third-Party Services

- ChatDev relies on OpenAI's API
- Review [OpenAI's security practices](https://openai.com/security)
- Be aware of data processing and retention policies

## Security Updates

Security updates will be released as soon as possible after a vulnerability is confirmed. Updates will be announced through:

- GitHub Security Advisories
- Release notes
- Project README

## Vulnerability Disclosure Timeline

1. **Day 0**: Vulnerability reported
2. **Day 1-2**: Initial acknowledgment
3. **Day 1-7**: Detailed response with timeline
4. **Day 7-30**: Investigation and patch development
5. **Day 30-60**: Patch release and disclosure

## Security Tools

We use the following tools to maintain code security:

- **Bandit**: Python security linter
- **Safety**: Dependency vulnerability scanner
- **CodeQL**: Semantic code analysis
- **Pre-commit hooks**: Automated security checks

## Compliance

ChatDev is designed for research and development purposes. If you plan to use it in production or with sensitive data:

- Conduct a thorough security audit
- Implement additional security controls
- Ensure compliance with relevant regulations (GDPR, CCPA, etc.)
- Consider data residency requirements

## Contact

For security concerns, please contact:
- Email: contact@camel-ai.org
- Security Advisory: [GitHub Security Advisories](https://github.com/OpenBMB/ChatDev/security/advisories)

## Acknowledgments

We appreciate the security research community's efforts in helping keep ChatDev secure. Contributors who report valid security issues will be acknowledged (with permission) in our security hall of fame.

---

*Last updated: 2024-01-10*
