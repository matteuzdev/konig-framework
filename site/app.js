/**
 * KONIG Framework — Enterprise Interactive Scripts
 * Zero dependências externas, alto desempenho e acessibilidade.
 */

// 1. Cópia do Comando CLI
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

// 2. Alternador de Tema (Light / Dark)
const themeToggle = document.getElementById('themeToggle');

if (themeToggle) {
  themeToggle.addEventListener('click', () => {
    const isDark = document.body.classList.toggle('theme-dark');
    document.body.classList.toggle('theme-light', !isDark);
    localStorage.setItem('konig_theme_pref', isDark ? 'dark' : 'light');
  });
}

// Restaura preferência salva
window.addEventListener('DOMContentLoaded', () => {
  const saved = localStorage.getItem('konig_theme_pref');
  if (saved === 'dark') {
    document.body.classList.add('theme-dark');
    document.body.classList.remove('theme-light');
  }
});

// 3. Abas de Código do Showcase
const snippets = {
  python: `from core.engine.meta_orchestrator import OnixMetaOrchestrator

# Inicialização do ONIX Master Orchestrator
onix = OnixMetaOrchestrator()

# Geração automática da arquitetura de um Squad
blueprint = onix.generate_squad_blueprint(
    squad_type="commercial_whatsapp",
    domain_goal="Qualificação e fechamento de contratos para serviços de saúde"
)

# Materialização de agentes, checklists e workflows declarativos no disco
squad_path = onix.scaffold_squad_files(blueprint)
print(f"Squad de alta conversão homologado em: {squad_path}")`,

  cli: `# Instalação e execução do ciclo industrial completo
$ pip install konig-framework

# Execução do squad técnico com validação de Quality Gates
$ konig run .agents full_development_lifecycle

# Execução do squad comercial com ponte WhatsApp ativa
$ konig run squads/sales inbound_lead_qualification

# Auditoria e execução estática de script no Sandbox
$ konig sandbox scripts/test_pipeline.py`,

  yaml: `name: commercial-whatsapp-delivery
version: 2.0.0
description: DAG de qualificação e fechamento de leads via WhatsApp corporativo

tasks:
  - id: qualify_lead
    assigned_agent: sdr
    required_gates: [sdr_qualification_gate]
    
  - id: negotiate_terms
    assigned_agent: closer
    depends_on: [qualify_lead]
    required_gates: [deal_closing_gate]
    
  - id: trigger_onboarding
    assigned_agent: cs_manager
    depends_on: [negotiate_terms]
    required_gates: [cs_retention_gate]`
};

function selectTab(tabKey) {
  const buttons = document.querySelectorAll('.tab-btn');
  buttons.forEach(btn => btn.classList.remove('active'));

  if (event && event.target) {
    event.target.classList.add('active');
  }

  const container = document.getElementById('codeContent');
  if (!container) return;

  const code = snippets[tabKey] || snippets.python;
  const lang = tabKey === 'cli' ? 'bash' : (tabKey === 'yaml' ? 'yaml' : 'python');

  container.innerHTML = `<pre><code class="language-${lang}">${escapeHtml(code)}</code></pre>`;
}

function escapeHtml(text) {
  return text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}
