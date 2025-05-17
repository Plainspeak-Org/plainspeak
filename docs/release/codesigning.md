# Binary Code Signing Guide

This document outlines the process for signing and notarizing PlainSpeak binaries for secure distribution.

## Windows Code Signing

### Prerequisites
- Windows EV Code Signing Certificate
- SignTool (part of Windows SDK)
- Built Windows executable and installer

### Process

1. **Certificate Installation**
   ```powershell
   # Import certificate
   certutil -importpfx SigningCert.pfx
   ```

2. **Sign Executable**
   ```powershell
   signtool sign /tr http://timestamp.digicert.com /td sha256 /fd sha256 /a "dist\plainspeak\plainspeak.exe"
   ```

3. **Sign Installer**
   ```powershell
   signtool sign /tr http://timestamp.digicert.com /td sha256 /fd sha256 /a "dist\PlainSpeak-Setup.exe"
   ```

4. **Verify Signatures**
   ```powershell
   signtool verify /pa "dist\plainspeak\plainspeak.exe"
   signtool verify /pa "dist\PlainSpeak-Setup.exe"
   ```

### GitHub Actions Integration
```yaml
- name: Sign Windows Binary
  env:
    CERTIFICATE_BASE64: ${{ secrets.WINDOWS_CERT_BASE64 }}
    CERTIFICATE_PASSWORD: ${{ secrets.WINDOWS_CERT_PASSWORD }}
  run: |
    echo $CERTIFICATE_BASE64 | base64 -d > certificate.pfx
    signtool sign /f certificate.pfx /p $CERTIFICATE_PASSWORD /tr http://timestamp.digicert.com /td sha256 /fd sha256 /a "dist\plainspeak\plainspeak.exe"
    signtool sign /f certificate.pfx /p $CERTIFICATE_PASSWORD /tr http://timestamp.digicert.com /td sha256 /fd sha256 /a "dist\PlainSpeak-Setup.exe"
```

## macOS Code Signing

### Prerequisites
- Apple Developer ID Certificate
- Apple Developer account
- Xcode command line tools
- Built macOS application bundle

### Process

1. **Certificate Setup**
   ```bash
   # List available certificates
   security find-identity -v -p codesigning
   ```

2. **Sign Application**
   ```bash
   # Sign the application bundle
   codesign --force --sign "Developer ID Application: PlainSpeak Organization" \
           --options runtime \
           --entitlements "installers/macos/entitlements.plist" \
           --timestamp \
           "dist/PlainSpeak.app"
   ```

3. **Verify Signature**
   ```bash
   codesign --verify --deep --strict "dist/PlainSpeak.app"
   spctl --assess --type execute --verbose=4 "dist/PlainSpeak.app"
   ```

### Notarization

1. **Create Archive**
   ```bash
   ditto -c -k --keepParent "dist/PlainSpeak.app" "dist/PlainSpeak.zip"
   ```

2. **Submit for Notarization**
   ```bash
   xcrun notarytool submit "dist/PlainSpeak.zip" \
         --apple-id "$APPLE_ID" \
         --password "$APP_SPECIFIC_PASSWORD" \
         --team-id "$TEAM_ID" \
         --wait
   ```

3. **Staple Notarization**
   ```bash
   xcrun stapler staple "dist/PlainSpeak.app"
   ```

### GitHub Actions Integration
```yaml
- name: Sign and Notarize macOS App
  env:
    APPLE_CERTIFICATE: ${{ secrets.MACOS_CERTIFICATE_BASE64 }}
    APPLE_CERTIFICATE_PASSWORD: ${{ secrets.MACOS_CERTIFICATE_PASSWORD }}
    APPLE_ID: ${{ secrets.APPLE_ID }}
    APPLE_TEAM_ID: ${{ secrets.APPLE_TEAM_ID }}
    APP_SPECIFIC_PASSWORD: ${{ secrets.APPLE_APP_PASSWORD }}
  run: |
    # Import certificate
    echo $APPLE_CERTIFICATE | base64 -d > certificate.p12
    security create-keychain -p "$KEYCHAIN_PASSWORD" build.keychain
    security import certificate.p12 -k build.keychain -P "$APPLE_CERTIFICATE_PASSWORD" -T /usr/bin/codesign
    
    # Sign
    codesign --force --sign "Developer ID Application: PlainSpeak Organization" \
            --options runtime \
            --entitlements "installers/macos/entitlements.plist" \
            --timestamp \
            "dist/PlainSpeak.app"
            
    # Notarize
    ditto -c -k --keepParent "dist/PlainSpeak.app" "dist/PlainSpeak.zip"
    xcrun notarytool submit "dist/PlainSpeak.zip" \
          --apple-id "$APPLE_ID" \
          --password "$APP_SPECIFIC_PASSWORD" \
          --team-id "$APPLE_TEAM_ID" \
          --wait
    xcrun stapler staple "dist/PlainSpeak.app"
```

## Required Files

### macOS Entitlements
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>com.apple.security.cs.allow-jit</key>
    <true/>
    <key>com.apple.security.cs.allow-unsigned-executable-memory</key>
    <true/>
    <key>com.apple.security.cs.disable-library-validation</key>
    <true/>
    <key>com.apple.security.cs.allow-dyld-environment-variables</key>
    <true/>
    <key>com.apple.security.automation.apple-events</key>
    <true/>
</dict>
</plist>
```

## Certificate Management

### Windows
1. Purchase EV Code Signing Certificate
2. Store certificate securely
3. Add to GitHub Secrets:
   - `WINDOWS_CERT_BASE64`
   - `WINDOWS_CERT_PASSWORD`

### macOS
1. Generate Developer ID Certificate
2. Create App-Specific Password
3. Add to GitHub Secrets:
   - `MACOS_CERTIFICATE_BASE64`
   - `MACOS_CERTIFICATE_PASSWORD`
   - `APPLE_ID`
   - `APPLE_TEAM_ID`
   - `APPLE_APP_PASSWORD`

## Verification Steps

### Windows
1. Check digital signature in properties
2. Verify with SignTool
3. Test SmartScreen response

### macOS
1. Verify code signature
2. Check notarization status
3. Test Gatekeeper response

## Distribution Checklist

- [ ] Binaries built successfully
- [ ] Code signing completed
- [ ] Notarization successful
- [ ] Signatures verified
- [ ] Test installation process
- [ ] Update documentation
- [ ] Create release notes
