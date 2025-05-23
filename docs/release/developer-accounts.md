# PlainSpeak Developer Portal Setup Guide

## PyPI Package Distribution

### Account Setup
1. Organization Account: cschanhniem
2. Multi-factor Authentication: Required
3. Project Name: plainspeak (registered and published)
4. PyPI URL: [https://pypi.org/project/plainspeak/](https://pypi.org/project/plainspeak/)
5. Trusted Publishers: Enabled
6. API Tokens: Generated per CI/CD pipeline

### Security Requirements
- OIDC-based authentication
- Reserved namespace protections
- Package signing with GPG
- Supply chain security measures
- Dependency pinning

### Publishing Process
1. Configure Poetry with PyPI token:
   ```bash
   poetry config pypi-token.pypi your-api-token
   ```
2. Build and publish:
   ```bash
   poetry publish --build
   ```

### Configuration Files
```toml
# pyproject.toml additions
[project]
name = "plainspeak"
version = "1.0.0"
description = "Turns everyday English into real terminal commands and API calls."
authors = [
    {name = "cschanhniem", email = "contact@plainspeak.pro"}
]
readme = "README.md"
license = {file = "LICENSE"}
requires-python = ">=3.9"
classifiers = [
    "Development Status :: 4 - Beta",
    "Environment :: Console",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3.9",
    "Topic :: Software Development :: Libraries :: Python Modules",
    "Topic :: System :: Shells"
]

[project.urls]
Homepage = "https://plainspeak.org"
Documentation = "https://docs.plainspeak.org"
Repository = "https://github.com/cschanhniem/plainspeak"
Changelog = "https://github.com/cschanhniem/plainspeak/blob/main/CHANGELOG.md"
```

## Microsoft Store

### Developer Account
1. Organization: PlainSpeak Organization
2. Account Type: Company Account
3. Verification Status: Verified Publisher
4. Store Identity: Secured

### App Registration
1. App Name: PlainSpeak
2. Category: Developer Tools
3. Package Identity: org.plainspeak.app
4. MSIX Configuration: Complete

### Store Presence
1. Store Listing Requirements:
   - Privacy Policy URL
   - Support Contact Info
   - Age Ratings
   - System Requirements
   - Feature Tags

2. Required Screenshots:
   - Feature Highlights (1366x768)
   - UI Details (1366x768)
   - Mobile/Tablet Views (if applicable)

3. Store Assets:
   - Logo (300x300)
   - Hero Image (1920x1080)
   - Feature Graphics (Various sizes)

## Apple App Store

### Developer Account
1. Organization: PlainSpeak Organization
2. Program Type: Company Developer
3. Team ID: PLAINSPK123
4. Certificates: Distribution & Development

### App Store Connect
1. Bundle ID: org.plainspeak.app
2. App Category: Developer Tools
3. Age Rating: 4+
4. Privacy Information: Completed

### Required Information
1. App Review Information:
   - Demo Account
   - Review Notes
   - Contact Information
   - Support URL

2. App Store Presence:
   - Description
   - Keywords
   - Support URL
   - Marketing URL
   - Privacy Policy URL

3. Store Assets:
   - App Icon (1024x1024)
   - Screenshots (Multiple sizes)
   - App Preview Videos

## Linux Package Repositories

### Package Maintainer Accounts
1. Debian: plainspeak-maintainers
2. Ubuntu: plainspeak-team
3. Fedora: plainspeak
4. AUR: plainspeak-maintainer

### Repository Keys
1. GPG Key Generation:
   ```bash
   gpg --full-generate-key
   # Key type: RSA and RSA
   # Key size: 4096 bits
   # Key validity: 2 years
   # Identity: PlainSpeak Package Maintainers <packages@plainspeak.org>
   ```

2. Key Distribution:
   - Published to keyservers
   - Added to repository metadata
   - Documented in release notes

### Package Metadata
```yaml
Package: plainspeak
Version: 0.1.0
Section: utils
Priority: optional
Architecture: any
Essential: no
Depends: python3 (>= 3.9)
Maintainer: PlainSpeak Package Maintainers <packages@plainspeak.org>
Description: Natural language interface for computing
 PlainSpeak transforms everyday language into precise computer operations,
 allowing anyone to interact with their machine using natural language.
 .
 Features:
  * Natural language command processing
  * Plugin system for extensibility
  * Cross-platform support
  * Offline-first design
Homepage: https://plainspeak.org
```

## Account Security

### Key Management
1. Hardware Security Keys required for all accounts
2. Backup security keys stored securely
3. Regular key rotation schedule
4. Access audit logging enabled

### Access Control
1. Role-based access for team members
2. Separate credentials per platform
3. Regular access audits
4. Security incident response plan

### Monitoring
1. Account activity monitoring
2. Automated security alerts
3. Regular security assessments
4. Compliance checking

## Documentation & Procedures

### Account Recovery
1. Primary contacts list
2. Recovery procedures
3. Emergency contact information
4. Backup authentication methods

### Maintenance Tasks
1. Quarterly security reviews
2. Certificate renewal tracking
3. Access permission audits
4. Compliance verification

### Team Onboarding
1. Access request process
2. Security training requirements
3. Role assignment procedures
4. NDA and security policies

## Emergency Procedures

### Account Compromise
1. Immediate response steps
2. Communication templates
3. Recovery procedures
4. Post-incident analysis

### Service Disruption
1. Backup distribution channels
2. Communication plan
3. Recovery checklist
4. Status monitoring

### Contact Information
- Security Team: security@plainspeak.org
- Legal Team: legal@plainspeak.org
- Support Team: support@plainspeak.org
- Emergency: +1-555-0123 (24/7)
