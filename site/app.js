/**
 * KONIG Framework — Enterprise Interactive Engine
 * Motion, Simuladores de DAG, WhatsApp Streaming, Waveforms e Spotlight.
 */

// ==============================================================================
// 1. CÓPIA E SELEÇÃO DE COMANDO CLI (HERO & QUICKSTART COM OS SYNC)
// ==============================================================================
let currentOs = 'win'; // 'win' | 'unix'
let currentHeroManager = 'uv'; // 'uv' | 'installer' | 'pip'

const cliCommandsMap = {
  uv: {
    win: 'uv pip install konig-framework; konig run .agents',
    unix: 'uv pip install konig-framework && konig run .agents'
  },
  installer: {
    win: 'git clone https://github.com/matteuzdev/konig-framework.git; cd konig-framework; python install.py',
    unix: 'git clone https://github.com/matteuzdev/konig-framework.git && cd konig-framework && python3 install.py'
  },
  pip: {
    win: 'pip install konig-framework; konig run .agents',
    unix: 'pip install konig-framework && konig run .agents'
  }
};

const qsSnippets = {
  uv: {
    win: `<span class="c-comment"># 1. Crie o ambiente virtual ultra-rápido e instale o pacote</span>\nuv venv; uv pip install konig-framework\n\n<span class="c-comment"># 2. Execute o squad autônomo de engenharia</span>\nkonig run .agents`,
    unix: `<span class="c-comment"># 1. Crie o ambiente virtual ultra-rápido e instale o pacote</span>\nuv venv && uv pip install konig-framework\n\n<span class="c-comment"># 2. Execute o squad autônomo de engenharia</span>\nkonig run .agents`
  },
  installer: {
    win: `<span class="c-comment"># 1. Clone o repositório oficial</span>\ngit clone https://github.com/matteuzdev/konig-framework.git\ncd konig-framework\n\n<span class="c-comment"># 2. Execute o assistente (detecta motor uv em Rust automaticamente)</span>\npython install.py`,
    unix: `<span class="c-comment"># 1. Clone o repositório oficial</span>\ngit clone https://github.com/matteuzdev/konig-framework.git\ncd konig-framework\n\n<span class="c-comment"># 2. Execute o assistente (detecta motor uv em Rust automaticamente)</span>\npython3 install.py`
  },
  pip: {
    win: `<span class="c-comment"># 1. Crie o ambiente virtual clássico</span>\npython -m venv .venv\n.venv\\Scripts\\activate\n\n<span class="c-comment"># 2. Instale o framework e rode o squad</span>\npip install konig-framework; konig run .agents`,
    unix: `<span class="c-comment"># 1. Crie o ambiente virtual clássico</span>\npython3 -m venv .venv\nsource .venv/bin/activate\n\n<span class="c-comment"># 2. Instale o framework e rode o squad</span>\npip install konig-framework && konig run .agents`
  }
};

function updateHeroDisplay() {
  const codeEl = document.getElementById('cliCommand');
  const promptEl = document.getElementById('cliPrompt');
  if (codeEl) {
    codeEl.innerText = cliCommandsMap[currentHeroManager][currentOs];
  }
  if (promptEl) {
    promptEl.innerText = currentOs === 'win' ? '>' : '$';
  }
}

function updateQsDisplay() {
  const tagLabels = {
    win: 'Windows PowerShell',
    unix: 'macOS / Linux (Bash)'
  };

  ['uv', 'installer', 'pip'].forEach(key => {
    const codeEl = document.getElementById(`qsCode${key.charAt(0).toUpperCase() + key.slice(1)}`);
    const tagEl = document.getElementById(`qsTag${key.charAt(0).toUpperCase() + key.slice(1)}`);
    if (codeEl && qsSnippets[key][currentOs]) {
      codeEl.innerHTML = qsSnippets[key][currentOs];
    }
    if (tagEl) {
      tagEl.innerText = tagLabels[currentOs];
    }
  });
}

function switchGlobalOs(os) {
  currentOs = os;
  
  const heroWin = document.getElementById('heroOsWin');
  const heroUnix = document.getElementById('heroOsUnix');
  if (heroWin && heroUnix) {
    heroWin.classList.toggle('active', os === 'win');
    heroUnix.classList.toggle('active', os === 'unix');
  }

  const qsWin = document.getElementById('qsOsWin');
  const qsUnix = document.getElementById('qsOsUnix');
  if (qsWin && qsUnix) {
    qsWin.classList.toggle('active', os === 'win');
    qsUnix.classList.toggle('active', os === 'unix');
  }

  updateHeroDisplay();
  updateQsDisplay();
}

function switchHeroManager(mgr) {
  currentHeroManager = mgr;
  ['uv', 'installer', 'pip'].forEach(m => {
    const btn = document.getElementById(`tabHero${m.charAt(0).toUpperCase() + m.slice(1)}`);
    if (btn) {
      btn.classList.toggle('active', m === mgr);
    }
  });
  updateHeroDisplay();
}

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
  if (saved !== 'light') {
    document.body.classList.add('theme-dark');
    document.body.classList.remove('theme-light');
  } else {
    document.body.classList.add('theme-light');
    document.body.classList.remove('theme-dark');
  }
  initWaveform();
  initCounters();
  initSpotlights();
  switchTgChannel('core');
  setTimeout(updateAllDagWires, 100);
});

window.addEventListener('load', () => {
  updateAllDagWires();
  setTimeout(updateAllDagWires, 250);
});

// ==============================================================================
// 3. TRAÇADO DINÂMICO DE CURVAS BÉZIER DO DAG (KRONOS)
// ==============================================================================
function drawDagWire(wireId, startPortId, endPortId) {
  const canvas = document.getElementById('dagCanvas');
  const wire = document.getElementById(wireId);
  const pStart = document.getElementById(startPortId);
  const pEnd = document.getElementById(endPortId);

  if (!canvas || !wire || !pStart || !pEnd) return;

  const canvasRect = canvas.getBoundingClientRect();
  const rStart = pStart.getBoundingClientRect();
  const rEnd = pEnd.getBoundingClientRect();

  // Coordenadas relativas ao canvas com ancoragem central precisa
  const x1 = (rStart.left + rStart.right) / 2 - canvasRect.left;
  const y1 = (rStart.top + rStart.bottom) / 2 - canvasRect.top;
  const x2 = (rEnd.left + rEnd.right) / 2 - canvasRect.left;
  const y2 = (rEnd.top + rEnd.bottom) / 2 - canvasRect.top;

  const dx = Math.max(Math.abs(x2 - x1) * 0.5, 40);
  const d = `M ${x1} ${y1} C ${x1 + dx} ${y1}, ${x2 - dx} ${y2}, ${x2} ${y2}`;
  wire.setAttribute('d', d);
}

function updateAllDagWires() {
  drawDagWire('wire-1-2a', 'port-1-out', 'port-2a-in');
  drawDagWire('wire-1-2b', 'port-1-out', 'port-2b-in');
  drawDagWire('wire-2a-3', 'port-2a-out', 'port-3-in');
  drawDagWire('wire-2b-3', 'port-2b-out', 'port-3-in');
  drawDagWire('wire-3-4', 'port-3-out', 'port-4-in');
}

window.addEventListener('resize', updateAllDagWires);

let isSimulating = false;

function runDagSimulation() {
  if (isSimulating) return;
  isSimulating = true;
  updateAllDagWires();

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

  const w1_2a = document.getElementById('wire-1-2a');
  const w1_2b = document.getElementById('wire-1-2b');
  const w2a_3 = document.getElementById('wire-2a-3');
  const w2b_3 = document.getElementById('wire-2b-3');
  const w3_4 = document.getElementById('wire-3-4');

  const m1 = document.getElementById('metric-1');
  const m2a = document.getElementById('metric-2a');
  const m2b = document.getElementById('metric-2b');
  const m3 = document.getElementById('metric-3');
  const m4 = document.getElementById('metric-4');

  // Wave 1: PM
  node1.className = 'dag-node-box running';
  m1.innerText = 'Refinando requisitos...';
  log.innerHTML += `<div class="log-line text-white">[WAVE 1] Sarah (PM) refinando requisitos e gerando PRD formal...</div>`;

  setTimeout(() => {
    node1.className = 'dag-node-box completed';
    m1.innerText = '[OK] PRD Aprovado (Score 1.0)';
    w1_2a.classList.add('active');
    w1_2b.classList.add('active');
    log.innerHTML += `<div class="log-line text-green">[WAVE 1] Gate de PRD aprovado. Handoff propagado para Wave 2.</div>`;

    // Wave 2: Paralela (Alex + Carol)
    node2a.className = 'dag-node-box parallel-node running';
    node2b.className = 'dag-node-box parallel-node running';
    m2a.innerText = 'Modelando endpoints...';
    m2b.innerText = 'Gerando tokens...';
    log.innerHTML += `<div class="log-line text-cyan">[WAVE 2 PARALELA] Alex (Arquiteto) & Carol (UI/UX) executando em paralelo...</div>`;

    setTimeout(() => {
      node2a.className = 'dag-node-box parallel-node completed';
      node2b.className = 'dag-node-box parallel-node completed';
      m2a.innerText = '[OK] OpenAPI Homologada';
      m2b.innerText = '[OK] Design System Pronto';
      w1_2a.className = 'dag-wire completed';
      w1_2b.className = 'dag-wire completed';
      w2a_3.classList.add('active');
      w2b_3.classList.add('active');
      log.innerHTML += `<div class="log-line text-green">[WAVE 2] Contratos de API e Design Tokens homologados. Handoff enviado ao time dev.</div>`;

      // Wave 3: Dev
      node3.className = 'dag-node-box running';
      m3.innerText = 'Compilando TypeScript...';
      log.innerHTML += `<div class="log-line text-white">[WAVE 3] Dan (Engenheiro) implementando código de produção com tipagem estrita...</div>`;

      setTimeout(() => {
        node3.className = 'dag-node-box completed';
        m3.innerText = '[OK] Build Concluído (0 errors)';
        w2a_3.className = 'dag-wire completed';
        w2b_3.className = 'dag-wire completed';
        w3_4.classList.add('active');
        log.innerHTML += `<div class="log-line text-green">[WAVE 3] Código compilado e submetido para validação formal em Sandbox.</div>`;

        // Wave 4: QA Sandbox
        node4.className = 'dag-node-box running';
        m4.innerText = 'Executando asserções AST...';
        log.innerHTML += `<div class="log-line text-cyan">[WAVE 4] Elena (QA) executando suíte de asserções no Sandbox isolado...</div>`;

        setTimeout(() => {
          node4.className = 'dag-node-box completed';
          m4.innerText = '[PASS] 14/14 Testes Passaram';
          w3_4.className = 'dag-wire completed';
          log.innerHTML += `<div class="log-line text-green">[WAVE 4] 100% dos testes aprovados no KonigSandbox (Exit Code: 0 | AST: Seguro).</div>`;
          log.innerHTML += `<div class="log-line text-white">[ONIX] Ciclo concluído com sucesso. Telemetria: 0.14s | Tokens: 1,420 | Status: Exit 0.</div>`;
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
  nodes.forEach(n => {
    n.className = n.classList.contains('parallel-node') ? 'dag-node-box parallel-node' : 'dag-node-box';
  });

  const wires = document.querySelectorAll('.dag-wire');
  wires.forEach(w => w.className = 'dag-wire');

  document.getElementById('metric-1').innerText = 'Aguardando disparo';
  document.getElementById('metric-2a').innerText = 'Em espera';
  document.getElementById('metric-2b').innerText = 'Em espera';
  document.getElementById('metric-3').innerText = 'Em espera';
  document.getElementById('metric-4').innerText = 'Em espera';

  const led = document.getElementById('simLed');
  led.classList.remove('active');

  const stateText = document.getElementById('simStateText');
  stateText.innerText = 'Pronto para disparar';

  const log = document.getElementById('simLog');
  log.innerHTML = `<div class="log-line text-muted">[ONIX] Simulador resetado. Aguardando novo ciclo.</div>`;

  const btn = document.getElementById('btnRunSim');
  btn.disabled = false;
  isSimulating = false;
  updateAllDagWires();
}

// ==============================================================================
// 4. WHATSAPP LIVE PLAYGROUND (STREAMING & TYPING INDICATOR)
// ==============================================================================
const waKnowledgeBase = {
  status: "Olá! O KONIG funciona como uma equipe completa de vendas e atendimento no seu WhatsApp. Ele recebe o cliente em 2 segundos com muita simpatia, explica o que sua empresa faz, responde dúvidas sobre produtos ou serviços e já envia a proposta ou link de pagamento — 24 horas por dia, sem você precisar ficar preso no celular!",
  falha: "Essa é a maior diferença do KONIG: ele tem uma trava de segurança blindada! A IA nunca inventa preços falsos, nunca promete prazos que você não pode cumprir e só fala o que foi aprovado na tabela da sua empresa. Se o cliente perguntar algo fora do padrão, o robô não mente: ele chama um atendente humano na hora!",
  metricas: "Sim, com certeza! O KONIG se conecta direto à sua agenda (Google Agenda, sistemas médicos, CRM ou planilhas). O cliente escolhe o melhor dia e horário pelo próprio WhatsApp, o sistema reserva o horário na hora e ainda manda mensagens automáticas de confirmação para ninguém esquecer!",
  handoff: "Se o cliente tiver um caso especial ou pedir para falar com uma pessoa, o KONIG aciona o seu time na hora no WhatsApp e já passa um resumo completo de tudo o que foi conversado. O cliente nem percebe a transição e você nunca perde uma venda!"
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

  // Seleciona resposta com base em palavras-chave técnicas
  let reply = waKnowledgeBase.status;
  const lower = userText.toLowerCase();

  if (lower.includes('falha') || lower.includes('ast') || lower.includes('erro') || lower.includes('diagnóstico') || lower.includes('diagnostico')) {
    reply = waKnowledgeBase.falha;
  } else if (lower.includes('token') || lower.includes('métrica') || lower.includes('metrica') || lower.includes('telemetria') || lower.includes('consumo') || lower.includes('dias')) {
    reply = waKnowledgeBase.metricas;
  } else if (lower.includes('handoff') || lower.includes('humano') || lower.includes('on-call') || lower.includes('intervenção') || lower.includes('intervencao')) {
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
    }, 12);

  }, 800);
}

// ==============================================================================
// 5. TELEGRAM MOBILE HUB & WAVEFORM
// ==============================================================================
const tgChannels = {
  core: {
    title: '# engenharia-core',
    msgs: [
      { agent: 'Sarah • Product Manager', text: 'Requisitos do novo gateway de faturamento aprovados com critérios de aceite determinísticos. Handoff emitido.' },
      { agent: 'Dan • Senior Engineer', text: 'Código desenvolvido com type hints e guardrails de timeout. Executando bateria de testes no Sandbox seguro.' },
      { agent: 'Elena • Staff QA', text: '[PASS] 14 testes unitários aprovados no KonigSandbox. Zero violações estáticas de AST. Pronto para branch main.' }
    ]
  },
  marketing: {
    title: '# squads-registry',
    msgs: [
      { agent: 'Registry • Orchestrator', text: 'Sincronização de squads concluída: 4 squads carregados a partir de .agents e squads/*.yaml.' },
      { agent: 'Schema Validator', text: 'Todos os schemas de agents e tasks validados com Pydantic v2 sem warnings.' }
    ]
  },
  sales: {
    title: '# pipeline-deploy',
    msgs: [
      { agent: 'CI/CD Pipeline', text: 'Container Docker montado com sucesso. MCP Server provisionado com porta isolada.' },
      { agent: 'Release Guardian', text: 'Tag v2.0.0 aprovada com Exit Code 0. Artefatos de build sincronizados no GitHub.' }
    ]
  },
  onix: {
    title: '# onix-governance',
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
<div class="c-line text-green">[OK] Squad de Engenharia (.agents): 5 Agentes | 5 Tasks | 1 Workflows</div>
<div class="c-line text-green">[OK] Squad de Marketing (squads/marketing): 3 Agentes | 3 Tasks | 1 Workflows</div>
<div class="c-line text-green">[OK] Squad de Vendas (squads/sales): 3 Agentes | 3 Tasks | 1 Workflows</div>
<div class="c-line text-green">[OK] Squad de Estratégia (squads/strategy): 2 Agentes | 2 Tasks | 1 Workflows</div>
<div class="c-line text-muted">Canais de Atendimento conectados: WhatsApp, Telegram, REST API, Webhooks</div>`,

  run: `<div class="c-line text-cyan">$ konig run .agents full_development_lifecycle</div>
<div class="c-line text-white">[EXEC] KONIG CLI — Iniciando execução de Squad: [.agents]</div>
<div class="c-line text-green">[OK] Wave 1: Sarah (PM) aprovou especificação de requisitos.</div>
<div class="c-line text-green">[OK] Wave 2: Alex (Arquiteto) & Carol (Design) homologaram contratos.</div>
<div class="c-line text-green">[OK] Wave 3: Dan (Engenheiro) compilou código tipado.</div>
<div class="c-line text-green">[OK] Wave 4: Elena (QA) aprovou no Sandbox isolado com Exit Code 0.</div>
<div class="c-line text-cyan">[SUCESSO] Execução finalizada com 100% de conformidade.</div>`,

  sandbox: `<div class="c-line text-cyan">$ konig sandbox scripts/test_pipeline.py</div>
<div class="c-line text-white">[AST-GUARD] KONIG AST Security Guardian: Analisando sintaxe estática...</div>
<div class="c-line text-green">[OK] Zero chamadas de sistema não autorizadas detectadas.</div>
<div class="c-line text-green">[OK] Subprocesso isolado iniciado com teto de memória e timeout de 15s.</div>
<div class="c-line text-white">Saída do Processo:</div>
<div class="c-line text-green">RAN 12 TESTS IN 0.18s — ALL PASSED (EXIT CODE 0)</div>`,

  benchmark: `<div class="c-line text-cyan">$ konig benchmark</div>
<div class="c-line text-white">MATRIZ INDUSTRIAL DE MATURIDADE:</div>
<div class="c-line text-green">[OK] Orquestração DAG Wave Engine: HOMOLOGADO</div>
<div class="c-line text-green">[OK] AST Sandbox Runtime Isolado: HOMOLOGADO</div>
<div class="c-line text-green">[OK] SYNAPSE Context Memory (4 Zonas): HOMOLOGADO</div>
<div class="c-line text-green">[OK] Omnichannel Nativo (Telegram & WhatsApp): HOMOLOGADO</div>
<div class="c-line text-cyan">[HOMOLOGADO] Veredito: Governança determinística de ponta a ponta sem alucinação.</div>`
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

// ==============================================================================
// 9. CURSOR GLOW & SCROLL PROGRESS (PADRÃO AIOX / SYNKRA ENGINE)
// ==============================================================================
window.addEventListener('scroll', () => {
  const scrollTop = window.scrollY || document.documentElement.scrollTop;
  const docHeight = document.documentElement.scrollHeight - window.innerHeight;
  const progressEl = document.getElementById('scrollProgress');
  if (progressEl && docHeight > 0) {
    progressEl.style.width = `${(scrollTop / docHeight) * 100}%`;
  }
});

const cursorGlow = document.getElementById('cursorGlow');
if (cursorGlow) {
  window.addEventListener('mousemove', (e) => {
    cursorGlow.style.left = `${e.clientX}px`;
    cursorGlow.style.top = `${e.clientY}px`;
  });
}

// ==============================================================================
// 10. QUICKSTART TABS & CODE COPY (UV, INSTALLER, PIP)
// ==============================================================================
function switchQsTab(tabKey) {
  const tabs = ['uv', 'installer', 'pip'];
  tabs.forEach(t => {
    const btn = document.getElementById(`qsTab${t.charAt(0).toUpperCase() + t.slice(1)}`);
    const panel = document.getElementById(`qsPanel${t.charAt(0).toUpperCase() + t.slice(1)}`);
    if (btn && panel) {
      if (t === tabKey) {
        btn.classList.add('active');
        panel.style.display = 'block';
      } else {
        btn.classList.remove('active');
        panel.style.display = 'none';
      }
    }
  });
}

function copyQsCode(tabKey) {
  const codeEl = document.getElementById(`qsCode${tabKey.charAt(0).toUpperCase() + tabKey.slice(1)}`);
  const labelEl = document.getElementById(`qsCopyLabel${tabKey.charAt(0).toUpperCase() + tabKey.slice(1)}`);
  if (!codeEl) return;

  const rawText = codeEl.innerText;
  navigator.clipboard.writeText(rawText).then(() => {
    if (labelEl) {
      labelEl.innerText = 'Copiado!';
      setTimeout(() => {
        labelEl.innerText = 'Copiar';
      }, 2000);
    }
  });
}

// ==============================================================================
// 10. INTERAÇÕES FLAGSHIP DO HYPER-ENGINE (AWWAARDSS SPEC)
// ==============================================================================
let ghostAccepted = false;
function acceptGhostText() {
  const ghost = document.getElementById('ghostCodeSnippet');
  const btn = document.getElementById('btnAcceptGhost');
  if (!ghost || !btn) return;

  ghostAccepted = !ghostAccepted;
  if (ghostAccepted) {
    ghost.classList.add('accepted');
    btn.innerText = '✨ Aceito sem mouse! (Tab)';
    btn.style.background = '#10B981';
    btn.style.color = '#FFFFFF';
  } else {
    ghost.classList.remove('accepted');
    btn.innerText = 'Pressione [Tab] para aceitar';
    btn.style.background = 'var(--accent-teal)';
    btn.style.color = '#030308';
  }
}

// Ouvinte de teclado global para a tecla Tab no editor Ghost Text
window.addEventListener('keydown', (e) => {
  if (e.key === 'Tab') {
    const editor = document.getElementById('editorCodeBody');
    if (editor && editor.getBoundingClientRect().top < window.innerHeight && editor.getBoundingClientRect().bottom > 0) {
      e.preventDefault();
      acceptGhostText();
    }
  }
});

function updateCostCalculator(runs) {
  const count = parseInt(runs, 10) || 1000;
  const sliderLabel = document.getElementById('sliderValLabel');
  const marketLabel = document.getElementById('marketCostLabel');
  const konigLabel = document.getElementById('konigCostLabel');
  const savingsBanner = document.getElementById('savingsBanner');

  if (sliderLabel) sliderLabel.innerText = `${count.toLocaleString('pt-BR')} runs`;

  const marketCost = count * 5.00;
  const konigCost = count * 0.0266;
  const savings = marketCost - konigCost;
  const savingsPercent = ((savings / marketCost) * 100).toFixed(2);

  if (marketLabel) marketLabel.innerText = `$${marketCost.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
  if (konigLabel) konigLabel.innerText = `$${konigCost.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
  if (savingsBanner) {
    savingsBanner.innerHTML = `⚡ Economia real: <b>$${savings.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} / mês</b> (${savingsPercent}% menos compute desperdiçado)`;
  }
}



// ==============================================================================
// 7. NAVEGAÇÃO MOBILE-FIRST (MENU HAMBURGUER ACESSÍVEL)
// ==============================================================================
function toggleMobileNav() {
  const drawer = document.getElementById('mobileNavDrawer');
  const btn = document.getElementById('mobileMenuBtn');
  if (drawer && btn) {
    const isOpen = drawer.classList.toggle('active');
    btn.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
  }
}
