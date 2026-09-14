# Contributing to SolsRNGCore

Thank you for your interest in contributing to **SolsRNGCore**! Whether you're fixing a bug, improving the UI, adding a feature, improving documentation, or helping test the project, contributions are welcome.

## Before You Contribute

Please read the project's [Code of Conduct](CODE_OF_CONDUCT.md) before participating.

SolsRNGCore is actively developed, so larger changes should generally be discussed before significant development begins. This helps avoid duplicated work and makes sure new features fit the project's architecture.

For small fixes, documentation improvements, and obvious bugs, you can generally submit a pull request directly.

## Ways to Contribute

There are many ways to help:

* 🐛 Report bugs
* 💡 Suggest features or improvements
* 🔧 Fix bugs
* ✨ Add new features
* 🎨 Improve the user interface
* 🧪 Add or improve tests
* 📖 Improve documentation
* 🔍 Review pull requests
* 🖥️ Help test on different platforms
* ⚡ Improve performance or reliability

## Reporting Bugs

When opening a bug report, please include as much useful information as possible.

Try to provide:

* What you expected to happen
* What actually happened
* Steps to reproduce the problem
* Your operating system
* Python version
* SolsRNGCore version or commit
* Relevant error messages or logs

**Do not include private information, authentication tokens, Discord webhook URLs, cookies, passwords, or other secrets in bug reports.**

## Suggesting Features

Feature requests are welcome!

When suggesting a feature, explain:

1. What the feature would do.
2. Why it would be useful.
3. How you think it could work, if you have an implementation idea.
4. Any potential drawbacks or compatibility concerns.

Features should fit the overall goals and architecture of SolsRNGCore.

## Pull Requests

Before opening a pull request:

1. Make sure your changes are based on the latest version of the relevant branch.
2. Test your changes locally.
3. Make sure existing functionality still works.
4. Keep the changes focused on the purpose of the pull request.
5. Remove personal configuration, generated files, caches, and other unnecessary files.
6. Do not commit secrets or private user data.

### Pull Request Titles

Use a clear and descriptive title.

Examples:

```text
Fix Discord webhook notification failure
Add automation retry handling
Improve biome detection
Update installation documentation
Fix profile configuration saving
```

### Pull Request Descriptions

Please explain:

* What changed
* Why it changed
* How it was tested
* Any known limitations or issues

If the pull request fixes an existing issue, reference that issue when appropriate.

## Code Style

Try to keep code:

* Readable
* Maintainable
* Consistent with the existing project
* Properly documented when necessary
* Organized according to the project's existing architecture

Avoid unnecessarily large rewrites when a smaller change can solve the problem.

New functionality should include appropriate tests whenever practical.

## Testing

Before submitting changes, test the affected functionality.

For Python changes, at minimum, consider running:

```bash
python -m py_compile ...
```

and the project's available test suite.

If your change affects a specific platform, backend, UI component, automation feature, or external integration, test that functionality directly when possible.

## Dependencies

Avoid adding dependencies unless they are actually necessary.

When adding a dependency:

* Explain why it is needed.
* Make sure it is compatible with the project's supported platforms.
* Prefer well-maintained and appropriately licensed packages.
* Update the project's dependency configuration as necessary.

## Security

**Never commit sensitive information.**

This includes:

* Discord webhook URLs
* API keys
* Access tokens
* Passwords
* Cookies
* Session data
* Private server links when they are user-specific
* Personal configuration files
* Machine-specific paths
* Other credentials or private data

If you discover a security vulnerability, avoid publicly posting sensitive details in an issue. Contact the project maintainers privately when possible.

## Documentation

Documentation improvements are always welcome.

When adding or changing functionality, update relevant documentation when appropriate so users and contributors can understand how the feature works.

## Community Contributions

Not every contribution has to be code.

Helping other users, testing releases, reporting reproducible bugs, improving documentation, and reviewing changes are all valuable contributions.

Please keep discussions constructive and respectful.

## Maintainer Review

All pull requests are subject to review.

Maintainers may request changes, ask questions, or suggest a different implementation. A pull request may also be declined if it conflicts with the project's goals, introduces unnecessary complexity, creates security or privacy concerns, or cannot be reasonably maintained.

Submitting a pull request does not guarantee that it will be merged.

## License

By contributing to SolsRNGCore, you agree that your contributions may be distributed under the project's existing license.

Thank you for helping make SolsRNGCore better! 💜
