# KONIG Framework — Arquitetura Industrial de Produção 2.0

O **KONIG Framework** é um motor industrial de orquestração de IA autônoma para engenharia de software e operações de negócios de alta performance. 

O ecossistema é alicerçado em 7 pilares proprietários:

1. **Protocolo de Handoff Estruturado:** Assinaturas visuais inequívocas (`[Nome - Papel]`), rastreabilidade de artefatos e contratos formais entre agentes.
2. **Barramento de Eventos e Execução em Waves:** Resolução de dependências via grafo acíclico dirigido (DAG com Algoritmo de Kahn) com paralelismo topológico.
3. **Quality Gates Industriais & Auto-Correção:** Avaliação determinística por checklists em markdown com loop autônomo de retries e refinamento contínuo.
4. **AST Security Guardian & Sandbox Runtime:** Execução de código em ambiente isolado com análise estática de sintaxe (AST) que bloqueia chamadas perigosas antes da execução.
5. **SYNAPSE Context Engine:** Monitoramento dinâmico em 4 zonas operacionais (`GREEN`, `YELLOW`, `ORANGE`, `RED`) e compressão semântica seletiva.
6. **LLM Router Resiliente com CostManager:** Fallback chain automático entre múltiplos provedores com cálculo financeiro de tokens e USD por chamada em tempo real.
7. **Omnichannel Single-Bot Multi-Agent Router:** Interface unificada via Telegram Fóruns (Topics por agente/squad) e notificações para WhatsApp móvel.

---

## 📂 1. Estrutura de Diretórios do Framework

O time de desenvolvimento de software de IA reside em [`.agents/`](file:///.agents/), isolado dos squads de negócio em [`squads/`](file:///squads/), acompanhado de adaptadores universais para ambientes de desenvolvimento:

```text
konig/
├── .agents/                    # TIME DE DESENVOLVIMENTO DE IA (UNIVERSAL CODING AGENTS)
│   ├── squad.yaml              # Manifesto do time técnico
│   ├── agents/                 # Agentes (.md): pm, architect, ui_ux_designer, engineer, qa_engineer
│   ├── tasks/                  # Tasks (.md): create-prd, design-architecture, design-ui-ux, implement-code, run-qa
│   ├── checklists/             # Quality Gates (.md): prd, architecture, ui-ux-pro-max, code-quality, qa
│   ├── templates/              # Templates (.md): prd, architecture, ui-ux-tokens, qa-report
│   └── workflows/              # DAGs (.yaml): greenfield-delivery.yaml
│
├── .cursor/                    # ADAPTADOR CURSOR IDE (rules/agents/*.mdc)
├── .claude/                    # ADAPTADOR CLAUDE CODE (commands/konig.md)
├── .antigravity/               # ADAPTADOR ANTIGRAVITY IDE (rules/konig-agents.md)
├── .codex/                     # ADAPTADOR OPENAI CODEX (instructions.md)
│
├── channels/                   # PONTES OMNICHANNEL (Telegram Forum Router & WhatsApp Bridge)
├── core/                       # NÚCLEO INDUSTRIAL
│   ├── engine/                 # Orchestrator, Environment, Synapse, SquadLoader, Gates
│   ├── llm/                    # Router com Fallback Chain
│   ├── memory/                 # CostManager e Auditor Financeiro
│   ├── primitives/             # Task, Workflow, Handoff, Gate, Message, Skill
│   └── runtime/                # Sandbox Isolado com AST Security Guardian
│
├── skills/                     # REGISTRY DE SKILLS & CAPACIDADES MODULARES
├── squads/                     # SQUADS DE NEGÓCIO
│   ├── marketing/              # CMO, Copywriter, Traffic & CRO Specialist
│   ├── sales/                  # SDR, Closer, Customer Success & Retention Lead
│   └── strategy/               # CEO Advisor, CFO & Unit Economics Guardian
│
├── cli.py                      # CLI INDUSTRIAL UNIFICADA (run, list, sandbox, matrix, telegram)
├── main.py                     # DEMONSTRAÇÃO END-TO-END DE PRODUÇÃO
└── pyproject.toml              # CONFIGURAÇÃO DE PACOTE E DEPENDÊNCIAS
```

---

## ⚡ 2. Motores de Execução (`core/`)

### 2.0 ONIX Master Orchestrator (`core/engine/meta_orchestrator.py`)
O **ONIX** é o cérebro de governança superior do KONIG. Ele é responsável por:
* **Geração Dinâmica de Squads:** Interpreta objetivos de alto nível e materializa agentes, checklists, templates e workflows sob demanda.
* **Supervisão Cross-Squad:** Sincroniza handoffs entre o time de engenharia (`.agents/`) e squads executivos (`squads/`).
* **KRONOS Wave Engine:** Coordena a resolução temporal de DAGs e a sincronização de barreiras paralelas.

### 2.1 Orquestrador DAG com Waves (`core/engine/orchestrator.py`)
Resolve as dependências das tarefas via ordenação topológica e divide a execução em **Waves**:
- **Wave 1:** `Product Requirements Document (PRD)` — *Lead Product Manager (Alice)*
- **Wave 2 (Paralela):** `System Architecture & API Design` (*Architect Bob*) + `UI/UX Pro-Max Design System` (*Designer Carol*)
- **Wave 3:** `Fullstack Core Implementation` — *Senior Fullstack Engineer (Dan)*
- **Wave 4:** `QA Automation & Security Homologation` — *Staff QA Engineer (Elena)*

### 2.2 Quality Gates Rígidos com Auto-Correção
- **`prd-gate-checklist`:** Garante personas, requisitos funcionais/não-funcionais, regras e critérios de aceite.
- **`architecture-gate-checklist`:** Valida endpoints RESTful, modularidade, diagramas e governança de segurança.
- **`ui-ux-pro-max-gate-checklist`:** Reprova sumariamente layouts simplórios; exige tipografia harmoniosa (Inter/Outfit), paleta HSL/Dark Mode, micro-interações e contraste WCAG AAA.
- **`code-quality-gate-checklist`:** Impede placeholders vazios (TODO/pass), valida tipagem estrita e tratamento de exceções.
- **`qa-gate-checklist`:** Valida cobertura de testes automatizados com asserções explícitas e validação em sandbox.

### 2.3 Sandbox Runtime Isolado (`core/runtime/sandbox.py`)
- **AST Security Guardian:** Analisa a árvore sintática abstrata antes de permitir a execução, bloqueando chamadas perigosas (`eval`, `exec`, módulos de kernel ou sistema).
- **Subprocesso Isolado:** Executa em diretório temporário restrito com timeout rígido e captura de stdout/stderr.

### 2.4 SYNAPSE Context Engine (`core/engine/synapse.py`)
- Rastreia a saturação da janela de contexto em 4 zonas operacionais.
- Ativa compressão semântica preservativa quando atinge limites críticos, mantendo blocos de código, contratos OpenAPI e requisitos funcionais.

---

## 📱 3. Conectividade Omnichannel (`channels/`)

- **Single-Bot Multi-Agent Router (`channels/telegram.py`):** Um único bot atende múltiplos squads no Telegram via fóruns/tópicos e menções diretas.
- **WhatsApp Bridge (`channels/whatsapp.py`):** Notificações móveis estruturadas para tomada de decisão em tempo real.
- **API Gateway (`channels/api.py`):** Endpoints FastAPI para integração com webhooks e pipelines externos.

---

## 🚀 4. Execução via CLI Unificada

```bash
# Listar todos os squads e agentes disponíveis
python cli.py list

# Executar o squad de engenharia em .agents
python cli.py run .agents greenfield-delivery

# Executar squad de marketing
python cli.py run squads/marketing funnel-launch

# Executar squad de vendas
python cli.py run squads/sales high-ticket-sales-pipeline

# Executar squad de estratégia
python cli.py run squads/strategy executive-planning

# Auditar e executar script Python no Sandbox seguro
python cli.py sandbox scratch/test_ast_clean.py
```
