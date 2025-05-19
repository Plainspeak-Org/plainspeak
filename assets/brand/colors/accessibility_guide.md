# PlainSpeak Color Accessibility Guide

## Overview

This guide ensures that PlainSpeak's color choices meet WCAG 2.1 accessibility standards, making our application usable by people with various visual impairments.

## Contrast Requirements

For text and interactive elements:

| Type | Minimum Contrast Ratio |
|------|------------------------|
| Normal Text (< 18pt) | 4.5:1 |
| Large Text (≥ 18pt or 14pt bold) | 3:1 |
| UI Components and Graphical Objects | 3:1 |

## Approved Color Combinations

### Text on Backgrounds

| Foreground | Background | Contrast Ratio | Passes AA | Passes AAA |
|------------|------------|----------------|-----------|------------|
| Light Gray (#E2E8F0) | Dark Slate (#2D3748) | 9.11:1 | ✅ | ✅ |
| Light Gray (#E2E8F0) | Darker Slate (#1A202C) | 13.39:1 | ✅ | ✅ |
| Dark Text (#2D3748) | Light Gray (#E2E8F0) | 9.11:1 | ✅ | ✅ |
| Primary Blue (#4299E1) | Darker Slate (#1A202C) | 4.84:1 | ✅ | ✅ |
| Success Green (#48BB78) | Darker Slate (#1A202C) | 5.02:1 | ✅ | ✅ |
| Medium Gray (#A0AEC0) | Darker Slate (#1A202C) | 4.13:1 | ✅ | ❌ |

### Interactive Elements

| Element | Foreground | Background | Contrast Ratio | Passes |
|---------|------------|------------|----------------|--------|
| Primary Button | White (#FFFFFF) | Primary Blue (#4299E1) | 3.04:1 | ✅ |
| Secondary Button | Primary Blue (#4299E1) | White (#FFFFFF) | 3.04:1 | ✅ |
| Links | Primary Blue (#4299E1) | Dark Slate (#2D3748) | 3.29:1 | ✅ |
| Focus Indicators | Accent Blue (#63B3ED) | Dark Slate (#2D3748) | 3.02:1 | ✅ |

## Color Blindness Considerations

### Deuteranopia (Red-Green Color Blindness)
- Avoid distinguishing information solely by red/green differences
- Use patterns, shapes, or labels in addition to color
- Primary Blue and Dark Slate remain distinguishable

### Protanopia (Red-Green Color Blindness)
- Success Green and Error Red may appear similar
- Always include icons or text labels with these colors

### Tritanopia (Blue-Yellow Color Blindness)
- Primary Blue and Success Green may be difficult to distinguish
- Use additional visual cues beyond color

## Implementation Guidelines

1. **Never use color alone** to convey information
2. **Provide text alternatives** for color-based indicators
3. **Test with color blindness simulators** during development
4. **Maintain sufficient contrast** between adjacent colors
5. **Use patterns or borders** to distinguish areas when colors might be similar

## Testing Tools

- [WebAIM Contrast Checker](https://webaim.org/resources/contrastchecker/)
- [Colorblinding Chrome Extension](https://chrome.google.com/webstore/detail/colorblinding/dgbgleaofjainknadoffbjkclicbbgaa)
- [Stark Figma Plugin](https://www.figma.com/community/plugin/732603254453395948/Stark)

## References

- [Web Content Accessibility Guidelines (WCAG) 2.1](https://www.w3.org/TR/WCAG21/)
- [Understanding Success Criterion 1.4.3: Contrast (Minimum)](https://www.w3.org/WAI/WCAG21/Understanding/contrast-minimum.html)
- [Understanding Success Criterion 1.4.11: Non-text Contrast](https://www.w3.org/WAI/WCAG21/Understanding/non-text-contrast.html)
