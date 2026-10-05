# Design Tokens & UI/UX Pro-Max: {{product_name}}

## 1. Tipografia (Google Fonts)
- **Primary Body Font:** Inter (weights: 400, 500, 600)
- **Display Heading Font:** Outfit (weights: 600, 700, 800)
- **Type Scale Ratio:** 1.25 (Major Third)
  - `h1`: 2.441rem (39.06px)
  - `h2`: 1.953rem (31.25px)
  - `h3`: 1.563rem (25.00px)
  - `base`: 1.000rem (16.00px)
  - `small`: 0.800rem (12.80px)

## 2. Paleta HSL & Dark Mode Tokens
```css
:root {
  /* Brand Primary */
  --primary-hue: 243;
  --primary-sat: 75%;
  --primary-light: 59%;
  --color-primary: hsl(var(--primary-hue), var(--primary-sat), var(--primary-light));
  
  /* Dark Mode Surfaces */
  --bg-dark: hsl(222, 47%, 11%);
  --surface-card: hsla(217, 33%, 17%, 0.75);
  --border-subtle: hsla(217, 33%, 25%, 0.5);
  
  /* Text Contrast */
  --text-high-contrast: hsl(210, 40%, 98%);
  --text-muted: hsl(215, 20%, 65%);
}
```

## 3. Micro-Interações & Easing
- **Button Hover:** `transform: scale(1.02); transition: all 200ms cubic-bezier(0.16, 1, 0.3, 1);`
- **Glassmorphism:** `backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);`
- **Focus Rings:** `box-shadow: 0 0 0 3px hsla(var(--primary-hue), var(--primary-sat), var(--primary-light), 0.35);`
