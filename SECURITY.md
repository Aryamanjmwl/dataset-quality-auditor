# Security Policy

## Supported Versions

Security fixes are handled on the default branch until the project publishes
versioned release support.

## Reporting a Vulnerability

Please do not open a public issue for a suspected security vulnerability.

Preferred reporting path:

1. Use GitHub private vulnerability reporting if it is enabled for this repository.
2. If private vulnerability reporting is not available, contact the maintainer privately through the maintainer's GitHub profile/contact route.
3. If no private contact route is available, open a minimal public issue asking for a private reporting path. Do not include exploit details, secrets, private data, or a full proof of concept in the public issue.

Include the following in a private report when possible:

- A short description of the issue.
- Steps to reproduce, if available.
- The affected version, commit, command, or workflow.
- Any relevant logs, screenshots, or proof of concept.
- Whether the issue could expose secrets, private datasets, generated reports, or local files.

The maintainer will review the report, confirm the impact where possible, and coordinate a fix before public disclosure.

## Scope

Security reports may include issues such as:

- Secret or credential exposure.
- Unsafe handling of local files or generated reports.
- Dependency or supply-chain risks.
- Command-line behaviour that could unexpectedly overwrite or expose files.
- AI review behaviour that could fabricate unsupported security claims.

For behaviour or community issues, use [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md) instead.
