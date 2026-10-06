/**
 * KONIG Framework — Enterprise Interactive Engine
 * Motion, Simuladores de DAG, WhatsApp Streaming, Waveforms e Spotlight.
 */

// ==============================================================================
// 1. CÓPIA DE COMANDO CLI
// ==============================================================================
function copyCli() {
  const codeEl = document.getElementById('cliCommand');
  const copyLabel = document.getElementById('copyLabel');
  const btn = document.getElementById('copyCliBtn');

  if (!codeEl) return;

  navigator.clipboard.writeText(codeEl.innerText).then(() => {
    copyLabel.innerText = 'Copiado';
    btn.style.borderColor = 'var(--accent-teal)';
    btn.style.color = 'var(--accent-teal)';

    setTimeout(() => {
      copyLabel.innerText = 'Copiar';
      btn.style.borderColor = '';
      btn.style.color = '';
    }, 2000);
  });
}

// ==============================================================================
// 2. ALTERNADOR DE TEMA (LIGHT / DARK)
// ==============================================================================
const themeToggle = document.getElementById('themeToggle');
if (themeToggle) {
  themeToggle.addEventListener('click', () => {
    const isDark = document.body.classList.toggle('theme-dark');
    document.body.classList.toggle('theme-light', !isDark);
    localStorage.setItem('konig_theme_pref', isDark ? 'dark' : 'light');
  });
}

window.addEventListener('DOMContentLoaded', () => {
  const saved = localStorage.getItem('konig_theme_pref');
  if (saved === 'dark') {
    document.body.classList.add('theme-dark');
    document.body.classList.remove('theme-light');
  }
  initWaveform();
  initCounters();
  initSpotlights();
  switchTgChannel('core');
});

// ==============================================================================
// 3. SIMULADOR DO ONIX WAVE ENGINE (KRONOS)
// ==============================================================================
let isSimulating = false;

function runDagSimulation() {
  if (isSimulating) return;
  isSimulating = true;

  const led = document.getElementById('simLed');
  const stateText = document.getElementById('simStateText');
  const btn = document.getElementById('btnRunSim');
  const log = document.getElementById('simLog');

  btn.disabled = true;
  led.classList.add('active');
  stateText.innerText = 'Executando DAG Topológico...';

  log.innerHTML = `<div class="log-line text-cyan">[ONIX] Disparo do pipeline KRONOS: resolvendo dependências via Algoritmo de Kahn...</div>`;

  const node1 = document.getElementById('node-wave-1');
  const node2a = document.getElementById('node-wave-2a');
  const node2b = document.getElementById('node-wave-2b');
  const node3 = document.getElementById('node-wave-3');
  const node4 = document.getElementById('node-wave-4');

  const l1_2a = document.getElementById('link-1-2a');
  const l1_2b = document.getElementById('link-1-2b');
  const l2a_3 = document.getElementById('link-2a-3');
  const l2b_3 = document.getElementById('link-2b-3');
  const l3_4 = document.getElementById('link-3-4');

  // Wave 1: PM
  node1.className = 'dag-node-box running';
  log.innerHTML += `<div class="log-line text-white">[WAVE 1] Sarah (PM) refinando requisitos e gerando PRD formal...</div>`;

  setTimeout(() => {
    node1.className = 'dag-node-box completed';
    l1_2a.classList.add('active');
    l1_2b.classList.add('active');
    log.innerHTML += `<div class="log-line text-green">[WAVE 1] Gate de PRD aprovado (Score: 1.0). Barreira de sincronização liberada.</div>`;

    // Wave 2: Paralela (Alex + Carol)
    node2a.className = 'dag-node-box running';
    node2b.className = 'dag-node-box running';
    log.innerHTML += `<div class="log-line text-cyan">[WAVE 2 PARALELA] Alex (Arquiteto) & Carol (UI/UX) executando em paralelo...</div>`;

    setTimeout(() => {
      node2a.className = 'dag-node-box completed';
      node2b.className = 'dag-node-box completed';
      l2a_3.classList.add('active');
      l2b_3.classList.add('active');
      log.innerHTML += `<div class="log-line text-green">[WAVE 2] Contratos de API e Design Tokens homologados. Handoff enviado ao time dev.</div>`;

      // Wave 3: Dev
      node3.className = 'dag-node-box running';
      log.innerHTML += `<div class="log-line text-white">[WAVE 3] Dan (Engenheiro) implementando código de produção com tipagem estrita...</div>`;

      setTimeout(() => {
        node3.className = 'dag-node-box completed';
        l3_4.classList.add('active');
        log.innerHTML += `<div class="log-line text-green">[WAVE 3] Código compilado e submetido para validação formal em Sandbox.</div>`;

        // Wave 4: QA Sandbox
        node4.className = 'dag-node-box running';
        log.innerHTML += `<div class="log-line text-cyan">[WAVE 4] Elena (QA) executando suíte de asserções no Sandbox isolado...</div>`;

        setTimeout(() => {
          node4.className = 'dag-node-box completed';
          log.innerHTML += `<div class="log-line text-green">✔ [WAVE 4] 100% dos testes aprovados no KonigSandbox (Exit Code: 0 | AST: Seguro).</div>`;
          log.innerHTML += `<div class="log-line text-white">🎉 [ONIX] Ciclo concluído com sucesso. Telemetria: 0.14s | Custo: $0.0031 USD.</div>`;
          stateText.innerText = 'Ciclo Finalizado com Sucesso (Exit Code 0)';
          btn.disabled = false;
          isSimulating = false;
        }, 1200);

      }, 1200);

    }, 1400);

  }, 1000);
}

function resetDagSimulation() {
  const nodes = document.querySelectorAll('.dag-node-box');
  nodes.forEach(n => n.className = 'dag-node-box');

  const links = document.querySelectorAll('.dag-link-line');
  links.forEach(l => l.className = 'dag-link-line');

  const led = document.getElementById('simLed');
  led.classList.remove('active');

  const stateText = document.getElementById('simStateText');
  stateText.innerText = 'Pronto para disparar';

  const log = document.getElementById('simLog');
  log.innerHTML = `<div class="log-line text-muted">[ONIX] Simulador resetado. Aguardando novo ciclo.</div>`;

  const btn = document.getElementById('btnRunSim');
  btn.disabled = false;
  isSimulating = false;
}

// ==============================================================================
// 4. WHATSAPP LIVE PLAYGROUND (STREAMING & TYPING INDICATOR)
// ==============================================================================
const waKnowledgeBase = {
  preco: "A consulta odontológica inicial com escaneamento digital 3D e raio-x panorâmico completo sai por R$ 180. Temos disponibilidade para amanhã às 09:30 e às 11:00 com o Dr. Marcos. Posso reservar o seu horário?",
  desconto: "Para pagamento à vista via Pix ou no pacote com limpeza preventiva, conseguimos fechar por R$ 150 já com o laudo completo entregue na hora! Quer que eu garanta o horário das 09:30 pra você agora?",
  convenio: "Trabalhamos na modalidade de livre escolha com emissão de nota fiscal e relatório descritivo para reembolso integral junto ao seu plano de saúde! Mais de 90% dos nossos pacientes conseguem reembolso rápido. Deseja agendar?",
  handoff: "Entendido! Já estou pausando o atendimento autônomo e transferindo nossa conversa com todo o seu histórico para a nossa coordenadora humana, Paula. Ela vai te responder por aqui em instantes."
};

function sendWaPreset(text) {
  sendWaUserMessage(text);
}

function handleWaInputKey(event) {
  if (event.key === 'Enter') {
    sendCustomWaMessage();
  }
}

function sendCustomWaMessage() {
  const input = document.getElementById('waCustomInput');
  const text = input.value.trim();
  if (!text) return;
  input.value = '';
  sendWaUserMessage(text);
}

function sendWaUserMessage(userText) {
  const chat = document.getElementById('waChatWindow');
  const now = new Date();
  const timeStr = `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}`;

  const userMsgEl = document.createElement('div');
  userMsgEl.className = 'wa-msg wa-out';
  userMsgEl.innerHTML = `<p>${escapeHtml(userText)}</p><span class="wa-time">${timeStr}</span>`;
  chat.appendChild(userMsgEl);
  chat.scrollTop = chat.scrollHeight;

  // Typing indicator
  const typing = document.getElementById('waTypingIndicator');
  const statusText = document.getElementById('waStatusText');
  typing.classList.add('active');
  statusText.innerText = 'digitando...';

  // Seleciona resposta com base em palavras-chave
  let reply = waKnowledgeBase.preco;
  const lower = userText.toLowerCase();

  if (lower.includes('desconto') || lower.includes('puxado') || lower.includes('caro')) {
    reply = waKnowledgeBase.desconto;
  } else if (lower.includes('convênio') || lower.includes('convenio') || lower.includes('reembolso')) {
    reply = waKnowledgeBase.convenio;
  } else if (lower.includes('humano') || lower.includes('atendente') || lower.includes('pessoa')) {
    reply = waKnowledgeBase.handoff;
  }

  // Simula latência de resposta e streaming
  setTimeout(() => {
    typing.classList.remove('active');
    statusText.innerText = 'online • Resposta em tempo real';

    const agentMsgEl = document.createElement('div');
    agentMsgEl.className = 'wa-msg wa-in';
    agentMsgEl.innerHTML = `<p></p><span class="wa-time">${timeStr}</span>`;
    chat.appendChild(agentMsgEl);

    // Efeito de digitação em streaming
    const p = agentMsgEl.querySelector('p');
    let i = 0;
    const interval = setInterval(() => {
      p.textContent += reply[i];
      i++;
      chat.scrollTop = chat.scrollHeight;
      if (i >= reply.length) {
        clearInterval(interval);
      }
    }, 14);

  }, 1000);
}

// ==============================================================================
// 5. TELEGRAM MOBILE HUB & WAVEFORM
// ==============================================================================
const tgChannels = {
  core: {
    title: '# 💻 engenharia-core',
    msgs: [
      { agent: 'Sarah • Product Manager', text: 'Requisitos do novo gateway de faturamento aprovados com critérios de aceite determinísticos. Handoff emitido.' },
      { agent: 'Dan • Senior Engineer', text: 'Código desenvolvido com type hints e guardrails de timeout. Executando bateria de testes no Sandbox seguro.' },
      { agent: 'Elena • Staff QA', text: '✔ 14 testes unitários aprovados no KonigSandbox. Zero violações estáticas de AST. Pronto para branch main.' }
    ]
  },
  marketing: {
    title: '# 🚀 growth-marketing',
    msgs: [
      { agent: 'Marcus • CMO', text: 'Estratégia de aquisição B2B estruturada. Canais validados: Google Ads Topo de Funil e Outbound SDR.' },
      { agent: 'Helena • Copywriter', text: 'Copy de alta conversão redigida com quebra de objeções sobre atendimento autônomo no WhatsApp.' }
    ]
  },
  sales: {
    title: '# 🤝 vendas-deals',
    msgs: [
      { agent: 'Lucas • SDR Lead', text: 'Qualificação de lead concluída: Clínica Sorriso Perfeito. Faturamento validado. Reunião agendada para amanhã às 14h.' },
      { agent: 'Roberto • Closer', text: 'Contrato de R$ 3.500 de implantação + R$ 800/mês de manutenção fechado em call de 25 minutos.' },
      { agent: 'Clara • Customer Success', text: 'Instância WhatsApp provisionada e entregue com checklist de onboarding finalizado.' }
    ]
  },
  onix: {
    title: '# 💎 onix-governance',
    msgs: [
      { agent: 'ONIX • Master Orchestrator', text: 'Supervisão ativa: 3 squads em paralelismo contínuo. SYNAPSE Context Memory operando com 18% de ocupação na Zona Verde.' },
      { agent: 'ONIX • Cost Manager', text: 'Auditoria financeira do ciclo: $0.18 USD consumidos. Trava de emergência íntegra.' }
    ]
  }
};

function switchTgChannel(key) {
  const btns = document.querySelectorAll('.tg-topic-btn');
  btns.forEach(b => b.classList.remove('active'));

  if (event && event.currentTarget) {
    event.currentTarget.classList.add('active');
  }

  const data = tgChannels[key] || tgChannels.core;
  document.getElementById('tgChannelTitle').innerText = data.title;

  const stream = document.getElementById('tgMessageStream');
  stream.style.opacity = '0';

  setTimeout(() => {
    stream.innerHTML = '';
    data.msgs.forEach(m => {
      const el = document.createElement('div');
      el.className = 'tg-stream-msg';
      el.innerHTML = `
        <div class="tg-msg-agent">${m.agent}</div>
        <p>${m.text}</p>
      `;
      stream.appendChild(el);
    });
    stream.style.opacity = '1';
  }, 120);
}

// Waveform interativa
function initWaveform() {
  const container = document.getElementById('waveformBars');
  if (!container) return;

  const heights = [6, 12, 18, 14, 22, 16, 20, 10, 15, 24, 18, 8, 14, 20, 12, 16, 22, 14, 8, 12, 18, 24, 16, 10];
  container.innerHTML = '';

  heights.forEach((h, idx) => {
    const bar = document.createElement('div');
    bar.className = 'wave-bar';
    bar.style.height = `${h}px`;
    bar.dataset.index = idx;
    container.appendChild(bar);
  });
}

let isPlayingVoice = false;
let voiceTimer = null;
let currentSec = 0;

function toggleVoiceAudio() {
  isPlayingVoice = !isPlayingVoice;
  const iconPlay = document.getElementById('iconPlay');
  const iconPause = document.getElementById('iconPause');
  const timeText = document.getElementById('voiceTime');
  const bars = document.querySelectorAll('.wave-bar');

  if (isPlayingVoice) {
    iconPlay.style.display = 'none';
    iconPause.style.display = 'block';

    voiceTimer = setInterval(() => {
      currentSec++;
      const min = Math.floor(currentSec / 60);
      const sec = currentSec % 60;
      timeText.innerText = `${min}:${String(sec).padStart(2, '0')} / 0:18`;

      const barIdx = Math.floor((currentSec / 18) * bars.length);
      bars.forEach((b, idx) => {
        b.classList.toggle('played', idx <= barIdx);
      });

      if (currentSec >= 18) {
        toggleVoiceAudio();
        currentSec = 0;
        bars.forEach(b => b.classList.remove('played'));
      }
    }, 1000);

  } else {
    iconPlay.style.display = 'block';
    iconPause.style.display = 'none';
    clearInterval(voiceTimer);
  }
}

// ==============================================================================
// 6. TERMINAL INTERATIVO DA CLI
// ==============================================================================
const termOutputs = {
  list: `<div class="c-line text-cyan">$ konig list</div>
<div class="c-line text-white">SQUADS DISPONÍVEIS NO KONIG FRAMEWORK:</div>
<div class="c-line text-green">✔ Squad de Engenharia (.agents): 5 Agentes | 5 Tasks | 1 Workflows</div>
<div class="c-line text-green">✔ Squad de Marketing (squads/marketing): 3 Agentes | 3 Tasks | 1 Workflows</div>
<div class="c-line text-green">✔ Squad de Vendas (squads/sales): 3 Agentes | 3 Tasks | 1 Workflows</div>
<div class="c-line text-green">✔ Squad de Estratégia (squads/strategy): 2 Agentes | 2 Tasks | 1 Workflows</div>
<div class="c-line text-muted">Adaptadores Multi-IDE ativos: .antigravity, .cursor, .claude, .codex, .vscode</div>`,

  run: `<div class="c-line text-cyan">$ konig run .agents full_development_lifecycle</div>
<div class="c-line text-white">🦁 KONIG CLI — Iniciando execução de Squad: [.agents]</div>
<div class="c-line text-green">✔ Wave 1: Sarah (PM) aprovou especificação de requisitos.</div>
<div class="c-line text-green">✔ Wave 2: Alex (Arquiteto) & Carol (Design) homologaram contratos.</div>
<div class="c-line text-green">✔ Wave 3: Dan (Engenheiro) compilou código tipado.</div>
<div class="c-line text-green">✔ Wave 4: Elena (QA) aprovou no Sandbox isolado com Exit Code 0.</div>
<div class="c-line text-cyan">🎉 Execução finalizada com 100% de conformidade.</div>`,

  sandbox: `<div class="c-line text-cyan">$ konig sandbox scripts/test_pipeline.py</div>
<div class="c-line text-white">🛡️ KONIG AST Security Guardian: Analisando sintaxe estática...</div>
<div class="c-line text-green">✔ Zero chamadas de sistema não autorizadas detectadas.</div>
<div class="c-line text-green">✔ Subprocesso isolado iniciado com teto de memória e timeout de 15s.</div>
<div class="c-line text-white">Saída do Processo:</div>
<div class="c-line text-green">RAN 12 TESTS IN 0.18s — ALL PASSED (EXIT CODE 0)</div>`,

  benchmark: `<div class="c-line text-cyan">$ konig benchmark</div>
<div class="c-line text-white">MATRIZ INDUSTRIAL DE MATURIDADE:</div>
<div class="c-line text-green">✔ Orquestração DAG Wave Engine: HOMOLOGADO</div>
<div class="c-line text-green">✔ AST Sandbox Runtime Isolado: HOMOLOGADO</div>
<div class="c-line text-green">✔ SYNAPSE Context Memory (4 Zonas): HOMOLOGADO</div>
<div class="c-line text-green">✔ Omnichannel Nativo (Telegram & WhatsApp): HOMOLOGADO</div>
<div class="c-line text-cyan">🏆 VEREDITO: Governança determinística de ponta a ponta sem alucinação.</div>`
};

function execTermCmd(cmdKey) {
  const btns = document.querySelectorAll('.btn-term-cmd');
  btns.forEach(b => b.classList.remove('active'));

  if (event && event.currentTarget) {
    event.currentTarget.classList.add('active');
  }

  const screen = document.getElementById('termConsole');
  screen.style.opacity = '0';

  setTimeout(() => {
    screen.innerHTML = termOutputs[cmdKey] || termOutputs.list;
    screen.style.opacity = '1';
  }, 100);
}

// ==============================================================================
// 7. SPOTLIGHT HOVER EFFECT (LINEAR / VERCEL STYLE)
// ==============================================================================
function initSpotlights() {
  const cards = document.querySelectorAll('.spotlight-card');
  cards.forEach(card => {
    card.addEventListener('mousemove', e => {
      const rect = card.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      card.style.setProperty('--mouse-x', `${x}px`);
      card.style.setProperty('--mouse-y', `${y}px`);
    });
  });
}

// ==============================================================================
// 8. CONTADORES NUMÉRICOS ANIMADOS
// ==============================================================================
function initCounters() {
  const counters = document.querySelectorAll('.counter');
  counters.forEach(c => {
    const target = parseInt(c.dataset.target, 10);
    let count = 0;
    const step = target / 30;

    const interval = setInterval(() => {
      count += step;
      if (count >= target) {
        c.innerText = `${target}%`;
        clearInterval(interval);
      } else {
        c.innerText = `${Math.floor(count)}%`;
      }
    }, 35);
  });
}

// Utilitário de escape HTML
function escapeHtml(text) {
  return text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}
