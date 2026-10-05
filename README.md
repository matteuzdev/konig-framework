<div align="center">

```
   _  ______  _  _____________   _______  ___   __  ________      ______  ___  __ __
  / |/ / __ \/ |/ /  _/ ___/ /  / __/ _ \/ _ | /  |/  / __/ | /| / / __ \/ _ \/ //_/
 /    / /_/ /    // // (_ / _ \/ _// , _/ __ |/ /|_/ / _/ | |/ |/ / /_/ / , _/ ,<   
/_/|_/\____/_/|_/___/\___/_//_/_/ /_/|_/_/ |_/_/  /_/___/ |__/|__/\____/_/|_/_/|_|  
```

# 👑 KONIG Agentic Framework
### *Industrial Autonomous Agent Orchestration Engine*
**Powered by ONIX Master Orchestrator**

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-emerald.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)
[![Status: Production Ready](https://img.shields.io/badge/Status-Industrial%20Grade-success.svg?style=for-the-badge)](ARCHITECTURE.md)
[![IDE Support](https://img.shields.io/badge/IDEs-Antigravity%20%7C%20Cursor%20%7C%20Claude%20%7C%20Codex-purple.svg?style=for-the-badge)](.antigravity/)

</div>

---

## 📌 O que é o KONIG?

O **KONIG Framework** é uma infraestrutura de orquestração autônoma de squads de Inteligência Artificial voltada para entregas industriais de alta complexidade.

Diferente de frameworks que dependem de loops reativos imprevisíveis ou prompts soltos em memória, o KONIG introduz uma **governança determinística baseada em DAGs (Directed Acyclic Graphs), Quality Gates automatizados com execução em Sandbox isolado e gestão ativa de contexto semântico.**

No coração do framework opera o **ONIX Master Orchestrator**, o regente supremo responsável pelo design, instanciação, sincronização de dependências entre squads e supervisão financeira em tempo real.

---

## ⚡ Por que o KONIG é Diferente? (Os 7 Pilares)

| Pilar Arquitetural | Problema em Frameworks Comuns | A Solução Definitiva do KONIG |
| :--- | :--- | :--- |
| **1. ONIX Wave Engine** | Loops caóticos, concorrência cega e alucinação em cadeia | Orquestração baseada em DAGs divididos em **Waves paralelas determinísticas** com barreiras de sincronia. |
| **2. AST Sandbox Guardrails** | Códigos gerados executam direto no host do desenvolvedor | **Ambiente isolado em subprocesso** com análise prévia de AST contra comandos destrutivos (`rm -rf`, `os.system`). |
| **3. SYNAPSE Context Memory** | Estouro de janela de contexto e esquecimento de regras | **4 Zonas semânticas com compressão seletiva de até 90%**, preservando contratos, APIs e código integralmente. |
| **4. Staff QA com Gates Reais** | O modelo afirma que "testou" sem rodar nenhum teste | O agente de QA **executa asserções reais no Sandbox**. Se o exit code for diferente de 0, o PR é reprovado. |
| **5. Suporte Universal a IDEs** | Preso a uma ferramenta ou a um web UI proprietário | Sincronização nativa out-of-the-box para **Antigravity, Cursor, Claude Code, OpenAI Codex e VS Code**. |
| **6. Omnichannel Integrado** | Bots isolados que exigem 1 webhook por agente | **Single-Bot Multi-Agent**: roteamento nativo em tópicos de fórum do Telegram e handoff para WhatsApp. |
| **7. Auditoria Financeira Real** | Contas surpresa de API e ausência de teto de gastos | Rastreio preciso de **tokens e custo em USD** em cada task, com corte automático ao atingir o budget estipulado. |

---

## 🚀 Instalação Rápida em 3 Passos

O KONIG conta com um assistente de instalação visual, didático e automatizado:

```bash
# 1. Clone o repositório
git clone https://github.com/matteuzdev/konig-framework.git
cd konig-framework

# 2. Execute o assistente de instalação interativo
python install.py

# 3. Explore os squads e comandos disponíveis
konig list
```

> **Dica**: Caso prefira instalação silenciosa e sem perguntas, execute:
> ```bash
> python install.py --yes
> ```

---

## 💻 Guia Prático de Comandos (CLI)

Após a instalação, o comando `konig` estará registrado globalmente em seu ambiente. Você também pode rodar diretamente via `python cli.py`.

### 1. Listar Recursos do Ecossistema
```bash
konig list
```
Exibe todos os squads disponíveis (`.agents`, `squads/marketing`, `squads/sales`), seus agentes especializados, skills carregadas e workflows homologados.

### 2. Executar o Ciclo Completo de Engenharia
```bash
konig run .agents full_development_lifecycle
```
Dispara a pipeline industrial:
1. **Sarah (Product Manager)** refina a especificação e define os Requisitos Funcionais.
2. **Alex (Software Architect)** desenha os diagramas de componentes e contratos de dados.
3. **Dan (Senior Software Engineer)** escreve o código de produção com type hints e docstrings.
4. **Elena (Staff QA Engineer)** escreve os testes unitários e valida no Sandbox isolado com exit code 0.

### 3. Executar Squads de Negócios e Vendas
```bash
# Funil de lançamento com CMO, Copywriter e Gestor de Tráfego
konig run squads/marketing launch_product_funnel

# Triagem e qualificação de leads B2B com SDR e Closer
konig run squads/sales inbound_lead_qualification
```

### 4. Executar Códigos de Forma Segura no Sandbox
```bash
konig sandbox caminho/do/seu_script.py
```

### 5. Comparativo e Benchmark Industrial
```bash
konig benchmark
```

---

## 📂 Estrutura do Repositório

```text
konig/
├── .agents/                    # Squad Principal de Engenharia de Software
│   ├── agents/                 # Sarah (PM), Alex (Architect), Dan (Dev), Elena (QA)
│   ├── workflows/              # DAGs de desenvolvimento, refatoração e bugfix
│   └── rules/                  # Regras operacionais da equipe de engenharia
├── .antigravity/               # Adaptadores e regras para Google Antigravity IDE
├── .claude/                    # Adaptadores e skills para Claude Code
├── .codex/                     # Adaptadores para OpenAI Codex
├── .cursor/                    # Regras de contexto para Cursor IDE
├── .vscode/                    # Configurações de workspace do VS Code
├── channels/                   # Pontes omnichannel (Telegram Fórum & WhatsApp)
├── core/
│   ├── engine/                 # KAISER Master Orchestrator, SquadLoader, SYNAPSE Memory
│   ├── llm/                    # Router com Fallback Chain inteligente e failover
│   ├── memory/                 # Gestor financeiro de tokens e custo em USD
│   ├── primitives/             # Modelos fundamentais (Task, Agent, Workflow)
│   └── runtime/                # Sandbox com análise AST e isolamento de subprocesso
├── skills/                     # Biblioteca de skills reutilizáveis
├── squads/                     # Squads de negócio (Marketing, Sales, Growth, etc.)
├── install.py                  # Assistente de instalação visual e interativo
├── cli.py                      # Interface de Linha de Comando (CLI)
├── setup.py                    # Script de empacotamento oficial
├── requirements.txt            # Dependências mínimas
├── .env.example                # Template didático de configuração de credenciais
└── ARCHITECTURE.md             # Especificação técnica e matemática profunda
```

---

## 💎 O ONIX Master Orchestrator

O **ONIX** é o motor de meta-orquestração do KONIG. Ele é capaz de ler qualquer demanda de negócio em linguagem natural e **auto-gerar um squad completo em segundos**:

```python
from core.engine.meta_orchestrator import OnixMetaOrchestrator

# Inicializa o ONIX
onix = OnixMetaOrchestrator()

# Gera a arquitetura completa de um novo Squad de Growth
blueprint = onix.generate_squad_blueprint(
    squad_type="growth",
    domain_goal="Escala de aquisição B2B internacional"
)

# Materializa os YAMLs de agentes e workflows no disco
squad_path = onix.scaffold_squad_files(blueprint)
print(f"Squad materializado em: {squad_path}")
```

---

## 🛡️ Segurança e Sandbox Runtime

Nenhum código gerado por IA deve ter permissão irrestrita de rodar na máquina host. O `KonigSandbox`:
1. **Analisa a Árvore Sintática Abstrata (AST)** do código antes da execução, bloqueando chamadas como `shutil.rmtree("/")`, `subprocess.Popen("format ...")` e acessos não autorizados.
2. Executa em **subprocesso isolado** com timeout rigoroso (padrão de 60s) e limites de memória.
3. Retorna saída estruturada (`stdout`, `stderr`, `exit_code`, `execution_time_ms`) diretamente para a asserção do agente de QA.

---

## 🤝 Como Contribuir

1. Faça um Fork do projeto.
2. Crie sua Feature Branch (`git checkout -b feature/novo-squad-financeiro`).
3. Commit suas mudanças (`git commit -m 'feat: adiciona squad de auditoria contabil'`).
4. Push para a Branch (`git push origin feature/novo-squad-financeiro`).
5. Abra um Pull Request.

---

## 📜 Licença

Distribuído sob a licença **MIT**. Veja [`LICENSE`](LICENSE) para mais detalhes.

---

<div align="center">
Desenvolvido com excelência técnica pelo <b>Ecossistema KONIG</b>.
</div>
