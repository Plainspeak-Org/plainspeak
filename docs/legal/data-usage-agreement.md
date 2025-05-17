# PlainSpeak Data Usage Agreement

*Last Updated: May 17, 2025*

## 1. Introduction

This Data Usage Agreement ("Agreement") outlines how PlainSpeak handles, processes, and protects data. Our core principle is local-only processing with complete user control.

## 2. Data Collection Policy

### 2.1 Core Principle: No External Data Collection
PlainSpeak explicitly DOES NOT:
- Collect user data
- Track usage patterns
- Monitor commands
- Share information
- Upload data to servers
- Use analytics
- Store user information

### 2.2 Local Data Storage
The following data is stored ONLY on your local device:

1. Command History
   - Location: `~/.plainspeak/history.db`
   - Purpose: Command recall and learning
   - Retention: User-controlled
   - Format: SQLite database

2. User Preferences
   - Location: `~/.plainspeak/config.yaml`
   - Purpose: Customization settings
   - Content: User preferences
   - Format: YAML file

3. Learning Data
   - Location: `~/.plainspeak/learning.db`
   - Purpose: Command improvement
   - Scope: Local patterns only
   - Format: SQLite database

## 3. Data Security

### 3.1 Local Security Measures
- AES-256 encryption at rest
- User-specific encryption keys
- Secure file permissions
- Resource isolation

### 3.2 Plugin Data Security
- Sandboxed execution
- Permission-based access
- Data isolation
- Secure defaults

## 4. User Control

### 4.1 Data Management Rights
Users can:
- View all stored data
- Export their data
- Delete their data
- Modify retention periods
- Control collection scope
- Disable features
- Reset learning data

### 4.2 Plugin Data Control
Users can:
- Allow/deny permissions
- Review data access
- Revoke access
- Delete plugin data

## 5. Data Processing

### 5.1 Local Processing
All processing occurs:
- On the local device
- Without internet access
- Within user constraints
- Under user control

### 5.2 Learning System
The learning system:
- Uses local data only
- Improves locally
- Maintains privacy
- Respects preferences

## 6. Data Retention

### 6.1 Default Retention
- Command history: 90 days
- Learning data: 180 days
- Logs: 30 days
- Temporary files: 24 hours

### 6.2 User Configuration
Users can:
- Modify retention periods
- Enable/disable retention
- Set custom policies
- Implement auto-deletion

## 7. Plugin Data Handling

### 7.1 Plugin Requirements
Plugins must:
- Declare data usage
- Request permissions
- Follow security rules
- Respect privacy

### 7.2 Plugin Restrictions
Plugins cannot:
- Access unauthorized data
- Share data externally
- Persist without permission
- Bypass restrictions

## 8. Data Export & Portability

### 8.1 Export Format
Data exports include:
- Command history (JSON)
- User preferences (YAML)
- Learning data (SQLite)
- Plugin data (JSON)

### 8.2 Export Process
Users can:
- Select data to export
- Choose export format
- Review before export
- Secure exports

## 9. Data Deletion

### 9.1 Deletion Rights
Users can delete:
- All local data
- Specific data types
- Time-based ranges
- Plugin data

### 9.2 Deletion Process
Deletion ensures:
- Complete removal
- Secure wiping
- Plugin cleanup
- Verification

## 10. Transparency

### 10.1 Data Locations
All data paths are:
- Clearly documented
- User-accessible
- Platform-specific
- Version-controlled

### 10.2 Data Documentation
We provide:
- Data schemas
- Storage details
- Access methods
- Security measures

## 11. Compliance

### 11.1 Privacy Standards
We comply with:
- GDPR principles
- CCPA requirements
- Privacy best practices
- Industry standards

### 11.2 Security Standards
We implement:
- Encryption standards
- Access controls
- Secure storage
- Data protection

## 12. Updates & Changes

### 12.1 Agreement Updates
Changes require:
- User notification
- Clear documentation
- Version tracking
- Update logs

### 12.2 Version History
We maintain:
- Change records
- Update notices
- Migration paths
- Archive copies

## 13. Contact Information

For data-related inquiries:
- Email: privacy@plainspeak.org
- GitHub: Open an issue
- Website: plainspeak.org/privacy

## 14. Acknowledgment

Using PlainSpeak indicates:
- Agreement to terms
- Understanding of rights
- Acceptance of local storage
- Control of your data

*This Agreement is open source and available at:
https://github.com/plainspeak-org/plainspeak/blob/main/docs/legal/data-usage-agreement.md*
