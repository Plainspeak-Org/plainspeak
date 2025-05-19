# PlainSpeak Color Palette

This directory contains color palette files and resources for the PlainSpeak brand.

## Primary Colors

| Color Name | Hex Code | RGB | Usage |
|------------|----------|-----|-------|
| Primary Blue | #4299E1 | rgb(66, 153, 225) | Main brand color, chat bubbles, interactive elements |
| Dark Slate | #2D3748 | rgb(45, 55, 72) | Background color, app icon, UI backgrounds |
| Success Green | #48BB78 | rgb(72, 187, 120) | Cursor, success indicators |
| Light Gray | #E2E8F0 | rgb(226, 232, 240) | Text, UI elements on dark backgrounds |

## Secondary Colors

| Color Name | Hex Code | RGB | Usage |
|------------|----------|-----|-------|
| Dark Blue | #2B6CB0 | rgb(43, 108, 176) | Borders, shadows |
| Accent Blue | #63B3ED | rgb(99, 179, 237) | Highlights, hover states |
| Medium Gray | #A0AEC0 | rgb(160, 174, 192) | Secondary text, UI elements |
| Darker Slate | #1A202C | rgb(26, 32, 44) | Contrasting elements |

## UI State Colors

| Color Name | Hex Code | RGB | Usage |
|------------|----------|-----|-------|
| Success | #48BB78 | rgb(72, 187, 120) | Confirmation, success states |
| Warning | #ECC94B | rgb(236, 201, 75) | Warning, caution states |
| Error | #F56565 | rgb(245, 101, 101) | Error, failure states |
| Info | #4299E1 | rgb(66, 153, 225) | Information, help states |

## Gradients

- Brand Gradient: `linear-gradient(135deg, #4299E1 0%, #2B6CB0 100%)`
- Dark Gradient: `linear-gradient(135deg, #2D3748 0%, #1A202C 100%)`
- Accent Gradient: `linear-gradient(135deg, #63B3ED 0%, #4299E1 100%)`

## CSS Variables

```css
:root {
  --primary: #4299E1;
  --background: #2D3748;
  --success: #48BB78;
  --text: #E2E8F0;
  --dark-blue: #2B6CB0;
  --accent-blue: #63B3ED;
  --medium-gray: #A0AEC0;
  --darker-slate: #1A202C;
  --warning: #ECC94B;
  --error: #F56565;
  --info: #4299E1;
}
```

## Usage Guidelines

1. Use Primary Blue for main CTAs and brand elements
2. Use Dark Slate for backgrounds and containers
3. Use Success Green sparingly for important indicators
4. Use Light Gray for most text on dark backgrounds
5. Apply gradients for visual hierarchy and depth
6. Maintain contrast ratios for accessibility (WCAG 2.1)
7. Use state colors consistently across the application

## Color Palette Files

This directory will contain:
- Color swatches in various formats (.ase, .clr, etc.)
- Color palette documentation
- Color usage examples
- Accessibility guidelines for color combinations
