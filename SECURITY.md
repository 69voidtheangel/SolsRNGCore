# Security Policy

## Supported Versions

Security fixes are generally prioritized for the latest version of SolsRNGCore.

| Version | Supported |
| ------- | --------- |
| Latest release | ✅ |
| Older releases | ⚠️ |
| Unreleased development versions | ⚠️ |

If you are using an older version, updating to the latest release is recommended before reporting a security issue.

## Reporting a Security Vulnerability

If you believe you have discovered a security vulnerability in SolsRNGCore, please **do not publicly disclose the vulnerability in a GitHub issue, discussion, pull request, or other public forum**.

Instead, contact the project maintainers privately through the available GitHub contact options.

When reporting a vulnerability, please include:

- A description of the vulnerability.
- The affected version or commit.
- Steps to reproduce the issue.
- The potential impact.
- Any relevant logs or error messages.
- A possible fix or mitigation, if you have one.

Please remove or redact sensitive information before sending logs or configuration files.

## Sensitive Information

Never publicly post or commit:

- Discord webhook URLs
- API keys
- Access tokens
- Passwords
- Authentication credentials
- Cookies
- Roblox session information
- Private server information
- Personal configuration files
- Machine-specific paths or information
- Any other private credentials or secrets

If sensitive information is accidentally committed, assume that the credential may be compromised and **rotate or revoke it immediately**.

Simply deleting the file in a later commit does not necessarily remove the information from Git history.

## Security Issues in Dependencies

SolsRNGCore relies on third-party software and Python packages.

If a security issue originates from a dependency rather than SolsRNGCore itself, please report the issue to the appropriate upstream project when possible, while also notifying the SolsRNGCore maintainers if the vulnerability affects SolsRNGCore users.

## Responsible Disclosure

Please give maintainers reasonable time to investigate and address a security vulnerability before publicly disclosing technical details.

Security reports will be reviewed and handled based on their severity and potential impact.

## Scope

This policy covers security vulnerabilities in:

- SolsRNGCore source code
- SolsRNGCore configuration and profile handling
- Authentication and credential handling
- Discord webhook functionality
- Automation functionality
- Data storage and configuration
- Dependencies when specifically used or configured by SolsRNGCore

Issues belonging entirely to external services are outside the project's direct control, but may still be reported if they create a security concern for SolsRNGCore users.

## Thank You

Responsible security research helps keep SolsRNGCore and its users safe.

Thank you for helping protect the project and its community.
