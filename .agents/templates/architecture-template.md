# Arquitetura do Sistema: {{system_name}}

## 1. Visão Geral de Componentes
- **Camada de Apresentação (Frontend):** {{frontend_stack}}
- **Gateway / API:** {{api_gateway_stack}}
- **Camada de Negócio / Serviços:** {{business_services}}
- **Camada de Dados & Persistência:** {{database_stack}}

## 2. Contratos de API (Endpoints Principais)
```yaml
openapi: 3.1.0
paths:
  /api/v1/{{resource_name}}:
    post:
      summary: {{endpoint_summary}}
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                {{property_definitions}}
      responses:
        '201':
          description: Criado com sucesso
```

## 3. Modelo de Dados (Entidades)
- **Tabela / Coleção:** `{{table_name}}`
  - `id`: UUID (Primary Key)
  - `created_at`: Timestamp (UTC)
  - `status`: String com enum indexado

## 4. Segurança e Governança
- **Autenticação:** {{auth_protocol}}
- **Controle de Acesso:** {{rbac_rules}}
