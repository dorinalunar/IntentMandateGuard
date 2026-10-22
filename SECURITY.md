# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| v2.0.x  | :white_check_mark: |

## Reporting a Vulnerability

Please do not open a public issue for security vulnerabilities. Contact the repository maintainer (`@dorinalunar`) directly via GitHub Security Advisories.

## Architectural Safeguards
- **Prompt Injection Defense**: All `intent` fields (`method`, `target`, `payload`) are canonicalized and evaluated strictly as untrusted data.
- **Unanimous High-Certainty Gate**: Tickets require `PASS` outcome and `solid` certainty across 100% of mandate rules.
- **Replay & Quota Protection**: Enforces per-mandate sequence nonces (`used_nonces`) and atomic quota locking prior to redemption.
