# Task: Design System & Interface Pro-Max

```yaml
task:
  id: design-ui-ux-pro-max
  title: Criação de Design System e Identidade Visual Pro-Max
  assigned_agent: ui_ux_designer
  depends_on:
    - create-prd
  required_gates:
    - ui-ux-pro-max-gate-checklist
  estimated_complexity: HIGH
  output_artifact: design_system.md
```

## 1. Objetivo
Criar uma especificação visual de nível extraordinário, anti-genérica e rigorosamente subordinada ao branding, arquétipo comercial e personas definidos no PRD, com design tokens semânticos, hierarquia tipográfica intencional e catálogo de micro-interações.

## 2. Passos de Execução
1. Analisar o DNA de Marca, o Arquétipo Comercial e as Personas definidos no PRD.
2. Selecionar e justificar o Arquétipo Estético do design (ex: Corporate Trust, Editorial Minimal, Tech High-Density, Human Playful, Bold Challenger).
3. Definir o sistema tipográfico (Display + Body) coerente com o tom de voz da marca, com escala modular proporcional.
4. Desenvolver a paleta semântica em HSL/CSS Variables (Brand Primary, Secondary, Background, Surfaces, Text, Muted, Status) e definir a política de superfícies (Light/Dark/Adaptive contextual).
5. Especificar estados interativos completos: default, hover (com easing suave), active, focus-visible, disabled e loading.
6. Garantir conformidade de contraste WCAG AAA/AA para todos os pares texto/fundo e densidade de informação.
7. Gerar a folha de tokens visuais e submeter ao Gate de UI/UX Pro-Max.

## 3. Critérios de Aceite
- [ ] Interface visual estritamente alinhada ao posicionamento de marca do cliente, sem templates genéricos.
- [ ] Especificações completas de micro-interações e transições funcionais.
- [ ] Tokens de design prontos para consumo por frontend em Tailwind / CSS Variables.
