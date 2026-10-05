# Task: Fechamento de Venda & Negociação de Alto Valor

```yaml
task:
  id: close-deal-negotiation
  title: Reunião de Fechamento e Quebra de Objeções
  assigned_agent: closer
  depends_on:
    - qualify-outbound-leads
  required_gates:
    - deal-closing-checklist
  estimated_complexity: HIGH
  output_artifact: signed_contract_summary.md
```

## 1. Objetivo
Conduzir a negociação comercial, ancorar o valor financeiro do produto e assinar o contrato.

## 2. Passos de Execução
1. Revisar o dossiê do lead preparado pelo SDR.
2. Conduzir a demonstração focada na dor do cliente (não no recurso técnico).
3. Apresentar os planos e o Retorno sobre Investimento (ROI) projetado.
4. Neutralizar objeções de preço, tempo ou equipe.
5. Fechar o acordo e emitir o contrato.
6. Submeter ao Checklist de Fechamento.
