# Design Tokens & UI/UX Pro-Max: {{product_name}}

## 1. Alinhamento de Marca & Arquétipo Estético
- **Brand Archetype:** {{brand_archetype}} (ex: Corporate Trust, Editorial Minimal, Tech High-Density, Human Playful, Bold Challenger)
- **Tom Visual:** {{visual_tone}} (ex: Sóbrio e confiável, Elegante e espaçado, Rápido e utilitário)
- **Modo Predominante de Uso:** {{surface_mode}} (Light / Dark / Adaptive contextual com base no ambiente do usuário)

## 2. Tipografia Intencional (Google Fonts / Variable Fonts)
- **Primary Body Font:** {{body_font}} (weights: 400, 500, 600)
- **Display Heading Font:** {{heading_font}} (weights: 600, 700, 800)
- **Type Scale Ratio:** {{type_scale_ratio}} (ex: 1.25 Major Third ou 1.20 Minor Third)
  - `h1`: {{h1_size}}
  - `h2`: {{h2_size}}
  - `h3`: {{h3_size}}
  - `base`: {{base_size}}
  - `small`: {{small_size}}

## 3. Paleta Semântica & Tokens de Superfície (HSL / CSS Variables)
```css
:root {
  /* Brand Core Tokens */
  --brand-primary: hsl({{primary_hue}}, {{primary_sat}}%, {{primary_light}}%);
  --brand-secondary: hsl({{secondary_hue}}, {{secondary_sat}}%, {{secondary_light}}%);
  --brand-accent: hsl({{accent_hue}}, {{accent_sat}}%, {{accent_light}}%);

  /* Contextual Surfaces */
  --bg-app: hsl({{bg_hue}}, {{bg_sat}}%, {{bg_light}}%);
  --surface-card: hsl({{card_hue}}, {{card_sat}}%, {{card_light}}%);
  --border-subtle: hsl({{border_hue}}, {{border_sat}}%, {{border_light}}%);

  /* Typography Contrast (WCAG AAA/AA) */
  --text-primary: hsl({{text_hue}}, {{text_sat}}%, {{text_light}}%);
  --text-muted: hsl({{muted_hue}}, {{muted_sat}}%, {{muted_light}}%);

  /* Feedback & Status */
  --status-success: hsl(142, 70%, 45%);
  --status-warning: hsl(38, 92%, 50%);
  --status-danger: hsl(0, 84%, 60%);
}
```

## 4. Micro-Interações & Usabilidade
- **Interactive Hover:** `transform: translateY(-1px); transition: all 180ms cubic-bezier(0.16, 1, 0.3, 1);`
- **Focus Rings (Acessibilidade):** `outline: 2px solid var(--brand-primary); outline-offset: 2px;`
- **Surface Elevation:** `box-shadow: 0 4px 12px -2px rgba(0, 0, 0, 0.08);`
