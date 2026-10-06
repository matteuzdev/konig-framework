/**
 * KONIG Framework — Interactive Web Scripts
 * Controla cópia de comandos, alternador de temas e tópicos do Telegram
 */

// 1. Cópia do Comando da Hero Section
function copyCommand() {
  const cmd = document.getElementById('cmdText').innerText;
  navigator.clipboard.writeText(cmd).then(() => {
    const copyBtn = document.getElementById('copyBtn');
    const copyText = document.getElementById('copyText');
    
    copyText.innerText = 'Copiado! ✔';
    copyBtn.style.backgroundColor = '#059669';
    copyBtn.style.color = '#FFFFFF';
    
    setTimeout(() => {
      copyText.innerText = 'Copiar';
      copyBtn.style.backgroundColor = '';
      copyBtn.style.color = '';
    }, 2500);
  });
}

// 2. Alternador de Tema Claro / Escuro
const themeToggle = document.getElementById('themeToggle');
const themeIcon = document.getElementById('themeIcon');

themeToggle.addEventListener('click', () => {
  if (document.body.classList.contains('theme-light')) {
    document.body.classList.remove('theme-light');
    document.body.classList.add('theme-dark');
    themeIcon.innerText = '☀️';
    localStorage.setItem('konig_theme', 'dark');
  } else {
    document.body.classList.remove('theme-dark');
    document.body.classList.add('theme-light');
    themeIcon.innerText = '🌙';
    localStorage.setItem('konig_theme', 'light');
  }
});

// Carrega preferência anterior
window.addEventListener('DOMContentLoaded', () => {
  const savedTheme = localStorage.getItem('konig_theme');
  if (savedTheme === 'dark') {
    document.body.classList.remove('theme-light');
    document.body.classList.add('theme-dark');
    themeIcon.innerText = '☀️';
  }
});

// 3. Simulação Dinâmica de Tópicos do Telegram
const topicFeeds = {
  dev: [
    { author: 'Sarah • Product Manager', cls: 'pm', text: 'Requisitos do novo módulo de pagamentos aprovados no PRD. Passando o bastão para o Arquiteto.', time: '14:02' },
    { author: 'Alex • Software Architect', cls: 'arch', text: 'Contrato de dados e diagrama de componentes desenhado. Sem falhas de idempotência. Dan, pode codar.', time: '14:04' },
    { author: 'Dan • Senior Engineer', cls: 'dev', text: 'Código implementado com type hints e tratamento de exceção. Elena, teste no Sandbox seguro.', time: '14:08' },
    { author: 'Elena • Staff QA', cls: 'qa', text: '✅ <strong>12 testes unitários executados no Sandbox isolado.</strong> Exit Code 0. Zero violações de AST. Pronto para deploy!', time: '14:10', success: true }
  ],
  marketing: [
    { author: 'Marcus • CMO', cls: 'pm', text: 'Definição da persona B2B e canais de tráfego (Google Ads Topo de Funil + Meta Retargeting). Helena, solte a copy.', time: '15:20' },
    { author: 'Helena • Copywriter', cls: 'dev', text: 'Headline validada com gatilho de mobilidade e ROI garantido. VSL estruturada com storytelling de dor.', time: '15:25' },
    { author: 'Leo • Traffic & CRO', cls: 'arch', text: 'Landing page conectada, eventos de conversão e pixel disparando perfeitamente. Subindo criativos.', time: '15:30', success: true }
  ],
  vendas: [
    { author: 'Lucas • SDR Lead', cls: 'pm', text: 'Lead qualificado via WhatsApp da Clínica Odonto Prime (faturamento anual > R$ 1.2M). Agendado demo para amanhã.', time: '16:05' },
    { author: 'Roberto • Closer', cls: 'qa', text: 'Call realizada. Objeção de implantação contornada com case de recuperação de pacientes. Proposta de R$ 3.800 + R$ 800/mês aceita.', time: '16:45', success: true },
    { author: 'Clara • CS & Retention', cls: 'arch', text: 'Onboarding iniciado no WhatsApp do cliente com checklist de boas-vindas. Primeiro valor entregue em 48h.', time: '16:50' }
  ],
  onix: [
    { author: 'ONIX • Master Orchestrator', cls: 'arch', text: '💎 <strong>Grafo de Governança Ativo:</strong> 3 squads operando em paralelo. Barramento SYNAPSE com 14% de saturação de contexto.', time: '17:00' },
    { author: 'ONIX • Cost Manager', cls: 'pm', text: 'Custo acumulado da operação: $0.14 USD. Teto de orçamento seguro ($5.00). Zero intervenções manuais.', time: '17:01', success: true }
  ]
};

function switchTopic(topicKey) {
  // Atualiza classe ativa dos botões
  const buttons = document.querySelectorAll('.tg-topic');
  buttons.forEach(btn => btn.classList.remove('active'));
  event.target.classList.add('active');

  const feedContainer = document.getElementById('tgFeed');
  feedContainer.style.opacity = '0';
  
  setTimeout(() => {
    feedContainer.innerHTML = '';
    const messages = topicFeeds[topicKey] || topicFeeds.dev;

    messages.forEach(msg => {
      const msgDiv = document.createElement('div');
      msgDiv.className = `tg-msg ${msg.success ? 'success' : ''}`;
      msgDiv.innerHTML = `
        <div class="tg-author-badge ${msg.cls}">${msg.author}</div>
        <p>${msg.text}</p>
        <span class="tg-timestamp">${msg.time}</span>
      `;
      feedContainer.appendChild(msgDiv);
    });

    feedContainer.style.opacity = '1';
  }, 150);
}
