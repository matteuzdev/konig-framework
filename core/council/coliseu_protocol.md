# PROTOCOLO DO COLISEU — Decisão Rígida, Execução Rápida
**Versão:** 1.0 | **Status:** Ativo | **Owner:** ONIX (Meta Orchestrator)

---

## PRINCÍPIOS INEGOCIÁVEIS

1. **Uma decisão por Coliseu.** Não "discussão aberta". Decide. Registra. Executa.
2. **5 fases, tempo fixo.** Fase 1-2 = 15min cada. Fase 3 = 20min. Fase 4 = 10min. Fase 5 = imediato.
3. **Voto = Responsabilidade.** Quem vota APOIA, executa. Quem vota OPÕE, documenta risco e mitigação.
4. **Condicional = Contrato.** "Apoia SE [condição específica, mensurável, prazo]." Não "apoia com ressalvas".
5. **Silêncio = Apoio.** Conselho não manifesta em 24h = apoia. ONIX executa.
6. **Revisão 7 dias.** Todo veredito tem auditoria obrigatória em 7 dias. "O que mudou? O veredito segura?"

---

## FASE 1: APRESENTAÇÃO (15 min)
**Owner:** ONIX | **Participantes:** Todos os 7 Conselheiros

### Input Obrigatório (Documento Único)
```markdown
# PROPOSTA COLISEU #[ID]
**Título:** [Uma frase. Ex: "Lançar Site+Automação para ICP=[Segmento] via Canal=[Canal]"]
**Contexto:** [Por que agora? Dados: HunterX score, pipeline, runway, feedback]
**Decisão Requerida:** [Binária: Sim/Não. Ou: Opção A vs B vs C]
**Opções:** [Máx 3. Cada uma com: Investimento, Prazo, Risco Principal, Payback estimado]
**Critérios de Sucesso:** [Métricas de INPUT (controllable) + OUTPUT (lagging) com targets]
**Deadline:** [Data dura para decisão]
```

### Dinâmica
1. ONIX lê o documento (3 min).
2. Cada Conselheiro faz **até 2 perguntas de esclarecimento** (não opinião). Total 12 min.
3. Perguntas fora do escopo = "Fase 2". ONIX corta.

---

## FASE 2: ATAQUE INDEPENDENTE (15 min)
**Owner:** Cada Conselheiro (paralelo, sem ver os outros) | **Output:** `analise_[conselheiro]_[id].md`

### Template Obrigatório por Conselheiro
```markdown
### ANÁLISE DE [NOME DO CONSELHEIRO]
**FRAMEWORK APLICADO:** [Seu framework principal — ex: Value Equation, Contrarian Truth, Inversion, etc.]
**PONTOS FORTES DA PROPOSTA:** [Máx 3. Baseados no SEU framework.]
**PONTOS FRACOS / RISCOS:** [Máx 3. Baseados no SEU framework.]
**DADOS FALTANTES:** [O que você PRECISA saber para votar. Específico.]
**VEREDITO INDIVIDUAL:** [APOIA | OPÕE | CONDICIONAL — com condição explícita]
**CONFIANÇA (1-5):** [5 = "Aposto minha reputação". 1 = "Chute no escuro".]
```

### Regras
- **Zero colaboração nesta fase.** Cada um pensa com SEU modelo mental.
- Salva em `docs/coliseu/analises/[id]/analise_[conselheiro]_[id].md`
- ONIX agrega automaticamente ao final dos 15 min.

---

## FASE 3: CONFRONTAÇÃO (20 min)
**Owner:** ONIX (modera) | **Participantes:** Todos os 7 (síncrono)

### Dinâmica
1. ONIX apresenta **Mapa de Convergência/Divergência** (auto-gerado das análises):
   - Votos: Apoia / Oposta / Condicional
   - Temas de risco convergentes (ex: 4/7 citaram "Canal não validado")
   - Condições sobrepostas (ex: 3/7 pedem "Garantia operacional por escrito")
2. **Rodada de Confrontação** (3 min por Conselheiro que votou OPÕE ou CONDICIONAL):
   - "Meu voto é [X] porque [framework]. Para mudar meu voto, precisaria ver [Y mensurável]."
   - Apoiadores podem questionar: "Seu risco [X] é mitigado por [Y da proposta]?"
3. **Síntese de ONIX** (2 min): "Consenso emergente = [X]. Ponto de bloqueio = [Y]. Próximo passo = [Z]."

---

## FASE 4: SÍNTESE & VEREDITO (10 min)
**Owner:** ONIX | **Output:** `veredito_[id].md`

### Vereditos Possíveis
| Veredito | Definição | Ação Imediata |
|----------|-----------|---------------|
| **APROVADO** | ≥5 APOIA, 0 OPÕE bloqueante | ONIX despacha tasks para squads |
| **APROVADO CONDICIONAL** | ≥5 APOIA/ CONDICIONAL, condições atendíveis em ≤48h | ONIX cria checklist de condições + owners + prazos |
| **REJEITADO** | ≥3 OPÕE com riscos não mitigáveis | ONIX arquiva. Registra lição. Próxima proposta incorpora. |
| **ESCALADO** | Empate / Risco existencial / Dados faltantes críticos | ONIX agenda "Coliseu Estendido" (dados + 48h) + define owner de cada dado |

### Formato do Veredito
```markdown
# VEREDITO COLISEU #[ID]
**Data:** [ISO 8601] | **Proposta:** [Título]
**VEREDITO:** [APROVADO | APROVADO CONDICIONAL | REJEITADO | ESCALADO]
**VOTAÇÃO:**
- Hill: [Apoia/Oppõe/Condicional] — Confiança: [1-5]
- Hormozi: [Apoia/Oppõe/Condicional] — Confiança: [1-5]
- Jobs: [Apoia/Oppõe/Condicional] — Confiança: [1-5]
- Munger: [Apoia/Oppõe/Condicional] — Confiança: [1-5]
- Thiel: [Apoia/Oppõe/Condicional] — Confiança: [1-5]
- Naval: [Apoia/Oppõe/Condicional] — Confiança: [1-5]
- Bezos: [Apoia/Oppõe/Condicional] — Confiança: [1-5]
**CONDIÇÕES (se aplicável):**
1. [Condição específica] — Owner: [Agent] — Prazo: [Data] — Critério de aceite: [Mensurável]
2. ...
**RISCOS ACEITOS:** [Lista. Cada um com: Mitigação + Owner + Monitoramento]
**TAREFAS DESPACHADAS:** [Lista de tasks ONIX → Squads com owner, prazo, definition of done]
**AUDITORIA AGENDADA:** [Data + 7 dias] — Owner: ONIX
```

---

## FASE 5: EXECUÇÃO & AUDITORIA (Contínuo)

### Execução Imediata (T0)
- ONIX cria tasks no formato KONIG (`task_create`, `task_assign`, `task_deadline`).
- Tasks têm: **Owner (Agent)**, **Definition of Done**, **Prazo**, **Métrica de Sucesso (Input)**.
- Squads recebem notificação + contexto (veredito + análises relevantes).

### Acompanhamento Diário (Standup ONIX)
- Input metrics por task (não "status"). Ex: "Demo scripts escritos: 3/5", "Garantia redigida: sim/não".
- Blocker = ONIX resolve em < 2h ou escala no Coliseu micro (15 min, conselheiros relevantes apenas).

### Auditoria Obrigatória (T+7 dias)
**Formato:** `auditoria_[id].md`
```markdown
# AUDITORIA COLISEU #[ID] — T+7
**Veredito Original:** [Link]
**O QUE ACONTECEU:** [Tasks concluídas / atrasadas / bloqueadas — dados reais]
**MÉTRICAS INPUT:** [Targets vs Realizado]
**MÉTRICAS OUTPUT (early):** [Leads, Demos, Conversões — se aplicável]
**VEREDITO SEGUROU?** [Sim / Parcial / Não — com evidência]
**LIÇÕES:** [O que o Conselho errou/acertou. Atualiza base de conhecimento.]
**PRÓXIMA AÇÃO:** [Dobrar / Pivotar / Matar / Escalar]
```

---

## VARIÁVEIS DE CONTEXTO (Preenchidas no Momento do Coliseu)

> **IMPORTANTE:** Estas NÃO são defaults. São placeholders que ONIX preenche ANTES da Fase 1.

| Variável | Descrição | Exemplo Preenchido |
|----------|-----------|-------------------|
| `{{ICP}}` | Perfil ideal de cliente (quem, dor, budget, autoridade) | "[A definir no Coliseu — ex hipotético: Donos de clínicas locais com agenda ociosa e budget R$ 1-3k/mês]" |
| `{{SEGMENTO}}` | Vertical de mercado | "[A definir no Coliseu — ex hipotético: Serviços locais de alto ticket]" |
| `{{CANAL}}` | Canal de aquisição primário | "[A definir no Coliseu — ex hipotético: Outreach consultivo direto + indicação via parceiros de software local]" |
| `{{MECANISMO_UNICO}}` | Unique Mechanism (Thiel/Jobs) | "HunterX Score: lead scoring proprietário com dados públicos + privados" |
| `{{OFERTA_GRAND_SLAM}}` | Oferta completa (Hormozi) | "Site 7 dias + Automação leads R$ 297/mo + Garantia: lead em 30 dias ou próximo grátis" |
| `{{RUNWAY_DIAS}}` | Dias de caixa restantes | 60 |
| `{{MRR_TARGET}}` | Meta de MRR no horizonte | R$ 20.000 |
| `{{HUNTERX_CAPACITY}}` | Capacidade atual do HunterX | "500 leads/dia, 50 scoreados, 10 qualified" |

---

## ESCALAÇÃO RÁPIDA (Micro-Coliseu)
Para decisões táticas (< R$ 5k, < 1 semana, reversíveis):
- ONIX + 2 Conselheiros relevantes (baseado no tema).
- 15 min total. Mesma estrutura condensada.
- Veredito vinculante. Auditoria em 3 dias.

---

## REGISTRO & CONHECIMENTO
- Todos os artefatos em `docs/coliseu/[YYYY-MM]/`
- Base de lições: `docs/coliseu/lessons-learned.md` (atualizada a cada auditoria).
- Padrões de voto por conselheiro: trackeados para calibrar confiança futura.