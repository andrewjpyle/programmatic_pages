# Security policy

## Supported versions

Pre-1.0, only the latest published version is supported. Security fixes will land in patch releases against the current minor.

## Reporting a vulnerability

Please **do not** open a public GitHub issue for security-sensitive reports.

Email: **andrew@andrewjpyle.com** with the subject line `[programmatic_pages SECURITY]`.

Include:

- A description of the vulnerability and its impact
- Steps to reproduce
- Affected version(s)
- Whether you'd like to be credited in the release notes

You should expect:

- An acknowledgement within ~3 business days
- A public fix released as soon as practical (typically within 14 days for non-critical issues, faster for actively exploitable ones)
- Credit in the release notes if you want it

## Scope

In scope:

- The Python package itself (`src/programmatic_pages/`)
- The management command's argument parsing
- The default Django template (`default.html`) — XSS, injection, etc.
- Schema.org JSON-LD output

Out of scope:

- Vulnerabilities in user-supplied templates, adapters, or page bodies — those are the consumer's responsibility
- Issues only reproducible with non-default Django settings that disable safe defaults (e.g., turning off auto-escape)
- Vulnerabilities in transitive dependencies that don't affect this package's surface
