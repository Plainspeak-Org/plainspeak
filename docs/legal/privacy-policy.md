# PlainSpeak Privacy Policy

*Last Updated: May 17, 2025*

## Our Commitment to Privacy

PlainSpeak is built with privacy as a fundamental principle. We believe your computing should be private, secure, and under your control.

## Overview

PlainSpeak is a 100% offline application. We do not:
- Collect any user data
- Track usage
- Require cloud connectivity
- Share any information

## Data Collection

### What We Collect
PlainSpeak does not collect, store, or transmit any personal information or usage data to external servers.

### Local Data Storage
The following data is stored locally on your device only:
- Command history (stored in `~/.plainspeak/history.db`)
- User preferences (stored in `~/.plainspeak/config.yaml`)
- Learning data (stored in `~/.plainspeak/learning.db`)

All local data storage is:
- Encrypted at rest
- Accessible only to the user
- Easily deleted by the user
- Never transmitted externally

### Optional Plugin Data
Some plugins may require access to:
- Local file system
- System commands
- Network access (if explicitly enabled)

All plugin permissions are:
- Explicitly requested
- User-approved
- Limited in scope
- Documented in plugin manifests

## Data Usage

### Local Processing
All natural language processing is performed:
- Entirely on your local device
- Using offline models
- Without cloud connectivity
- Within user-defined resource limits

### Command Execution
Commands are:
- Previewed before execution
- Executed locally
- Never logged externally
- Subject to user confirmation

## User Control

### Data Access
Users can:
- View all stored data
- Export their data
- Delete their data
- Control data retention

### Configuration
Users can:
- Enable/disable features
- Configure privacy settings
- Manage plugin permissions
- Set resource limits

## Security

### Local Security
PlainSpeak implements:
- Local file encryption
- Secure permission handling
- Resource isolation
- Plugin sandboxing

### Network Security
By default, PlainSpeak:
- Does not connect to the internet
- Does not open network ports
- Does not accept remote connections
- Requires explicit user action for network features

## Children's Privacy

PlainSpeak is not directed at children under 13. We do not:
- Collect age information
- Target children
- Allow age-restricted content
- Market to minors

## Changes to Privacy Policy

We will notify users of privacy policy changes through:
- Application updates
- GitHub repository
- Documentation site
- Release notes

## Your Rights

You have the right to:
- Access your data
- Delete your data
- Control your data
- Use PlainSpeak privately

## Contact Information

For privacy questions:
- Email: privacy@plainspeak.org
- GitHub: Open an issue
- Website: plainspeak.org/privacy

## Compliance

### GDPR Compliance
PlainSpeak is GDPR-compliant by design:
- No personal data collection
- No data transfer
- Full user control
- Local processing only

### CCPA Compliance
PlainSpeak exceeds CCPA requirements:
- No data sale
- No data sharing
- No data collection
- Complete user control

## Open Source Commitment

As an open-source project, we:
- Maintain transparent practices
- Welcome privacy audits
- Accept community feedback
- Prioritize user privacy

## Technical Details

### Data Storage Locations
```
~/.plainspeak/
├── config.yaml      # User preferences
├── history.db      # Command history
└── learning.db     # Learning data
```

### Plugin Data
```
~/.plainspeak/plugins/
└── {plugin_name}/
    └── data/       # Plugin-specific data
```

### Encryption
- AES-256 for data at rest
- User-specific encryption keys
- Local key storage only
- No remote key transmission

## Verification

Our privacy practices are:
- Open source and auditable
- Community-reviewed
- Technically verified
- Regularly assessed

## Developer Guidelines

For plugin developers:
- Respect user privacy
- Document data usage
- Implement secure practices
- Follow privacy guidelines

## Acknowledgment

By using PlainSpeak, you acknowledge:
- This privacy policy
- Local data storage
- User responsibility
- Plugin permissions

*This privacy policy is open source and available at:
https://github.com/plainspeak-org/plainspeak/blob/main/docs/legal/privacy-policy.md*
