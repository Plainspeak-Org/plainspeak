# Package Submission PR

## Description
This PR prepares a new package release for submission to distribution channels.

## Version Details
- Version Number: <!-- e.g., 0.1.0 -->
- Release Type: <!-- major/minor/patch -->
- Target Channels: <!-- list channels: PyPI, Windows Store, Mac App Store, etc. -->

## Checklist
Before submitting this PR, please verify:

### Version & Documentation
- [ ] Version numbers updated in all files:
  - [ ] `pyproject.toml`
  - [ ] `plainspeak/__init__.py`
  - [ ] `assets/VERSION.txt`
- [ ] Changelog updated
- [ ] Release notes prepared

### Assets & Listings
- [ ] Store listings reviewed and updated
- [ ] Screenshots and assets verified
- [ ] Legal documents current and compliant

### Build & Package
- [ ] Local build successful
- [ ] Test workflow ran successfully
- [ ] Binary packages generated and tested:
  - [ ] Windows (.exe, MSIX)
  - [ ] macOS (.app, DMG)
  - [ ] Linux (.deb, .rpm, PKGBUILD)

### Testing
- [ ] Unit tests passing
- [ ] Integration tests passing
- [ ] Binary tests passing
- [ ] Manual verification completed

### Security & Compliance
- [ ] Code signing certificates valid
- [ ] Security scan completed
- [ ] Privacy policy compliance verified
- [ ] Store guideline requirements met

### Pre-submission
- [ ] All GitHub Actions workflows passing
- [ ] Test submission workflow successful
- [ ] Store review requirements addressed

## Test Results
<!-- Include links to test runs and results -->
- Binary Tests: <!-- link -->
- Package Tests: <!-- link -->
- Validation Results: <!-- link -->

## Related Issues
- Closes #<!-- issue number -->

## Notes
<!-- Any additional information or special considerations -->
