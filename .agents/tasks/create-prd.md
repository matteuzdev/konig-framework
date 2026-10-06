# Task: Criação de PRD Enterprise

```yaml
task:
  id: create-prd
  title: Elaboração de Documento de Requisitos de Produto
  assigned_agent: pm
  required_gates:
    - prd-gate-checklist
  estimated_complexity: MEDIUM
  output_artifact: prd.md
```

## 1. Objetivo
Mapear com precisão o problema do usuário, os objetivos de negócio, a Topologia de Marca (DNA, arquétipo comercial, tom de voz e demografia de usuário), os requisitos funcionais (RF) e não funcionais (RNF), e os critérios de aceite verificáveis.

## 2. Passos de Execução
1. Analisar a demanda bruta enviada pelo solicitante e o modelo de negócio do produto.
2. Definir a Topologia de Marca: Arquétipo Comercial, Tom de Voz, Proposta Única de Valor (UVP) e Perfil Demográfico/Cognitivo do usuário.
3. Especificar os Requisitos Funcionais (RF) com identificadores únicos (ex: RF01, RF02).
4. Especificar os Requisitos Não Funcionais (RNF) com metas mensuráveis (latência, concorrência, segurança).
5. Preencher o template oficial localizado em `templates/prd-template.md`.
6. Submeter o documento final ao Quality Gate `checklists/prd-gate-checklist.md`.

## 3. Critérios de Aceite
- [ ] Topologia de Marca e Demografia claramente caracterizadas para alimentar UI/UX e Engenharia.
- [ ] Escopo claramente delimitado (In Scope vs Out of Scope).
- [ ] Requisitos com critérios de aceite no formato Given/When/Then.
- [ ] Assinatura formal de handoff anexada ao final do documento.
