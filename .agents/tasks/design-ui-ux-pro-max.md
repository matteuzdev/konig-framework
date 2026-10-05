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
Criar uma especificação visual de nível extraordinário, anti-genérica, com design tokens em HSL, hierarquia tipográfica precisa, paleta harmônica com Dark Mode nativo e catálogo de micro-interações.

## 2. Passos de Execução
1. Analisar as personas e o propósito do produto definidos no PRD.
2. Definir o par tipográfico contemporâneo (ex: Inter / Outfit / Plus Jakarta Sans) com escala modular 1.25.
3. Desenvolver a paleta de cores curada em HSL (primária vibrante, acentos contrastantes, superfícies de Dark Mode e Glassmorphism translúcido).
4. Especificar estados interativos completos: default, hover (com easing suave), active, disabled e loading.
5. Garantir conformidade de contraste WCAG AAA para todos os pares texto/fundo.
6. Gerar a folha de tokens visuais e submeter ao Gate de UI/UX Pro-Max.

## 3. Critérios de Aceite
- [ ] Interface visual sem nenhum traço de layout genérico ou básico.
- [ ] Especificações completas de micro-animações (durations, easings, transitions).
- [ ] Tokens de design prontos para consumo por frontend em Tailwind / CSS Variables.
