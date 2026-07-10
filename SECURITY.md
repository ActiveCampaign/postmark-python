# Security Policy

## Supported Versions

| Version | Supported |
| ------- | --------- |
| Latest  | Yes       |
| Older   | No        |

Only the latest published release receives security fixes. We recommend always pinning to the latest version.

## Reporting a Vulnerability

**Do not open a public GitHub issue for security vulnerabilities.**

Use GitHub's private vulnerability reporting:

1. Go to the [Security tab](https://github.com/ActiveCampaign/postmark-python/security)
2. Click **"Report a vulnerability"**
3. Fill in the details and submit

You'll receive an acknowledgement within **48 hours** and a triage response within **7 days**.

## Scope

**In scope:**
- Vulnerabilities in this SDK's Python code
- Vulnerable transitive dependencies pulled in by this package

**Out of scope:**
- Bugs in the Postmark service or API itself — report those to [Postmark support](https://postmarkapp.com/support)
- Issues requiring a compromised Postmark API token (treat tokens as secrets)
- Vulnerabilities in your application code that happens to use this SDK

## Responsible Disclosure

We ask that you:
- Give us reasonable time to fix the issue before public disclosure
- Avoid accessing or modifying data belonging to other users
- Not perform denial-of-service attacks

We commit to:
- Acknowledge your report promptly
- Keep you informed of our progress
- Credit you in the release notes (unless you prefer otherwise)
