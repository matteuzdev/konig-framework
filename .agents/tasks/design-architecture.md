# Task: Design de Arquitetura & Contratos de API

```yaml
task:
  id: design-architecture
  title: Especificação Técnica e Modelagem Arquitetural
  assigned_agent: architect
  depends_on:
    - create-prd
  required_gates:
    - architecture-gate-checklist
  estimated_complexity: HIGH
  output_artifact: architecture.md
```

## 1. Objetivo
Transformar os requisitos do PRD em um design de sistema escalável, desacoplado, seguro e com contratos de API padronizados.

## 2. Passos de Execução
1. Analisar os requisitos funcionais e não-funcionais do PRD.
2. Definir a divisão modular e os limites de contexto (Context Boundaries).
3. Projetar os contratos de API (REST/OpenAPI ou GraphQL) com payloads de request/response e códigos de status HTTP.
4. Modelar o schema de banco de dados (entidades, relacionamentos, índices de busca e idempotência).
5. Estabelecer as regras de segurança (autenticação JWT, autorização RBAC, rate limiting).
6. Preencher `templates/architecture-template.md` e submeter ao Quality Gate de Arquitetura.

## 3. Critérios de Aceite
- [ ] Endpoints de API completamente especificados com schemas JSON.
- [ ] Modelos de banco de dados sem dependências circulares.
- [ ] Tratamento de falha e planos de resiliência documentados.
