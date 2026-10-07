"""
KONIG Sales, Hosting & MRR CRM — FastAPI Server & Interactive Kanban UI.

Projetado por:
- Bob (Arquitetura & APIs)
- Carol (Design System, Tokens HSL & Micro-interações)
- Dan (Implementação Fullstack)
- Elena (Homologação & Qualidade)
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, Field

from crm.database import (
    init_db,
    list_deals,
    get_deal,
    create_deal,
    update_deal_stage,
    get_crm_metrics,
)

app = FastAPI(title="KONIG Sales & MRR CRM", version="2.0.0")

# Inicializa o banco no startup
@app.on_event("startup")
def on_startup():
    init_db()


class DealCreate(BaseModel):
    name: str = Field(..., description="Nome da confeitaria / ateliê")
    instagram: Optional[str] = Field("", description="@ do Instagram")
    whatsapp: str = Field(..., description="WhatsApp com DDI e DDD (ex: 5511999998888)")
    niche: Optional[str] = Field("Confeitaria Gourmet", description="Nicho de atuação")
    specialty: Optional[str] = Field("", description="Especialidade (ex: bolos festivos, doces)")
    deal_value: Optional[float] = Field(699.0, description="Valor do front-end")
    mrr_value: Optional[float] = Field(59.0, description="Valor da hospedagem recorrente mensal")
    hosting_domain: Optional[str] = Field("", description="Domínio do cliente")
    notes: Optional[str] = Field("", description="Anotações e dores da cliente")


class StageUpdate(BaseModel):
    stage: str = Field(..., description="Novo estágio do pipeline")


@app.get("/api/deals")
def api_list_deals():
    return list_deals()


@app.post("/api/deals")
def api_create_deal(deal: DealCreate):
    deal_id = create_deal(deal.model_dump())
    return {"success": True, "id": deal_id}


@app.patch("/api/deals/{deal_id}/stage")
def api_update_stage(deal_id: int, update: StageUpdate):
    ok = update_deal_stage(deal_id, update.stage)
    if not ok:
        raise HTTPException(status_code=404, detail="Lead não encontrado")
    return {"success": True, "stage": update.stage}


@app.get("/api/metrics")
def api_metrics():
    return get_crm_metrics()


@app.get("/api/upsell-script/{deal_id}")
def api_upsell_script(deal_id: int):
    deal = get_deal(deal_id)
    if not deal:
        raise HTTPException(status_code=404, detail="Lead não encontrado")
    
    name = deal["name"]
    first_name = name.split()[0]
    mrr = deal["mrr_value"] or 59.0
    
    script = (
        f"Oi {first_name}, tudo bem? Aqui é da equipe técnica do seu site!\n\n"
        f"A sua página tá rodando no nosso servidor seguro há alguns dias e analisamos que várias pessoas "
        f"já acessaram o seu cardápio pelo link da bio do Instagram.\n\n"
        f"Identificamos que muitas clientes deixam pra pedir bolo em cima da hora e às vezes esquecem a data da festa. "
        f"Nós criamos uma automação por IA que conecta no seu site e avisa a cliente 3 dias antes da festa "
        f"com um lembrete no WhatsApp pra ela confirmar o pedido.\n\n"
        f"Como você já é nossa cliente na hospedagem de R$ {int(mrr)}/mês, a gente consegue ativar esse módulo "
        f"de Lembrete de Festas por apenas R$ 47/mês a mais. Quer que eu ative pra rodar um teste no seu cardápio essa semana?"
    )
    
    return {
        "deal_id": deal_id,
        "name": name,
        "upsell_name": "Lembrete Automático de Encomendas & Festas (IA)",
        "script": script
    }


@app.get("/", response_class=HTMLResponse)
def serve_kanban_dashboard():
    """Interface visual do CRM projetada com os Design Tokens de Carol."""
    html_content = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>KONIG CRM — Vendas, Hospedagem & MRR</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;700&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg-app: #0B0F17;
      --bg-surface: #111827;
      --bg-card: #182234;
      --border-subtle: #223049;
      --border-focus: #3B82F6;
      
      --text-main: #F3F4F6;
      --text-muted: #9CA3AF;
      --text-bright: #FFFFFF;
      
      --primary: #3B82F6;
      --primary-hover: #2563EB;
      --success: #10B981;
      --success-bg: rgba(16, 185, 129, 0.12);
      --warning: #F59E0B;
      --warning-bg: rgba(245, 158, 11, 0.12);
      --danger: #EF4444;
      --purple: #8B5CF6;
      --purple-bg: rgba(139, 92, 246, 0.14);
      
      --shadow-sm: 0 2px 4px rgba(0,0,0,0.25);
      --shadow-md: 0 6px 16px rgba(0,0,0,0.35);
      --radius: 10px;
    }

    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: 'Plus Jakarta Sans', -apple-system, sans-serif;
      background-color: var(--bg-app);
      color: var(--text-main);
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      overflow-x: auto;
    }

    /* Top Navigation */
    header {
      background: var(--bg-surface);
      border-bottom: 1px solid var(--border-subtle);
      padding: 16px 24px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      position: sticky;
      top: 0;
      z-index: 50;
    }
    .brand {
      display: flex;
      align-items: center;
      gap: 12px;
    }
    .brand-icon {
      font-size: 24px;
      background: linear-gradient(135deg, #1E3A8A, #3B82F6);
      padding: 6px 10px;
      border-radius: 8px;
    }
    .brand-title {
      font-weight: 800;
      font-size: 1.15rem;
      letter-spacing: -0.02em;
    }
    .brand-sub {
      font-size: 0.75rem;
      color: var(--text-muted);
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }

    .btn {
      padding: 8px 16px;
      border-radius: 8px;
      font-weight: 600;
      font-size: 0.85rem;
      cursor: pointer;
      border: none;
      transition: all 0.2s ease;
      display: inline-flex;
      align-items: center;
      gap: 6px;
      font-family: inherit;
    }
    .btn-primary {
      background: var(--primary);
      color: white;
    }
    .btn-primary:hover { background: var(--primary-hover); transform: translateY(-1px); }
    .btn-success { background: var(--success); color: #022c22; font-weight: 700; }
    .btn-outline {
      background: transparent;
      border: 1px solid var(--border-subtle);
      color: var(--text-main);
    }
    .btn-outline:hover { background: var(--bg-card); }

    /* Metrics Bar */
    .metrics-bar {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 16px;
      padding: 20px 24px 10px;
    }
    .metric-card {
      background: var(--bg-surface);
      border: 1px solid var(--border-subtle);
      border-radius: var(--radius);
      padding: 16px 20px;
      display: flex;
      flex-direction: column;
      gap: 4px;
      box-shadow: var(--shadow-sm);
    }
    .metric-label {
      font-size: 0.75rem;
      font-weight: 600;
      color: var(--text-muted);
      text-transform: uppercase;
      letter-spacing: 0.04em;
    }
    .metric-value {
      font-size: 1.6rem;
      font-weight: 800;
      font-family: 'JetBrains Mono', monospace;
      letter-spacing: -0.02em;
    }
    .metric-sub {
      font-size: 0.75rem;
      color: var(--text-muted);
    }
    .val-green { color: var(--success); }
    .val-blue { color: var(--primary); }
    .val-purple { color: var(--purple); }

    /* Kanban Board */
    .kanban-wrapper {
      padding: 16px 24px 32px;
      flex: 1;
      display: flex;
      gap: 16px;
      overflow-x: auto;
      align-items: flex-start;
    }
    .kanban-column {
      background: var(--bg-surface);
      border: 1px solid var(--border-subtle);
      border-radius: var(--radius);
      min-width: 310px;
      max-width: 310px;
      display: flex;
      flex-direction: column;
      max-height: calc(100vh - 210px);
      box-shadow: var(--shadow-sm);
    }
    .column-header {
      padding: 14px 16px;
      border-bottom: 1px solid var(--border-subtle);
      display: flex;
      justify-content: space-between;
      align-items: center;
      background: rgba(255, 255, 255, 0.015);
      border-top-left-radius: var(--radius);
      border-top-right-radius: var(--radius);
    }
    .col-title-wrap {
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .col-dot {
      width: 10px;
      height: 10px;
      border-radius: 50%;
    }
    .col-title {
      font-weight: 700;
      font-size: 0.88rem;
      letter-spacing: -0.01em;
    }
    .col-count {
      background: var(--bg-card);
      border: 1px solid var(--border-subtle);
      font-size: 0.75rem;
      font-weight: 700;
      padding: 2px 8px;
      border-radius: 20px;
      color: var(--text-muted);
    }

    .cards-container {
      padding: 12px;
      overflow-y: auto;
      display: flex;
      flex-direction: column;
      gap: 12px;
      flex: 1;
    }

    /* Kanban Card */
    .deal-card {
      background: var(--bg-card);
      border: 1px solid var(--border-subtle);
      border-radius: 8px;
      padding: 14px;
      display: flex;
      flex-direction: column;
      gap: 10px;
      box-shadow: var(--shadow-sm);
      transition: all 0.2s ease;
      cursor: default;
    }
    .deal-card:hover {
      border-color: #3b82f688;
      transform: translateY(-2px);
      box-shadow: var(--shadow-md);
    }
    .card-head {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      gap: 6px;
    }
    .card-name {
      font-weight: 700;
      font-size: 0.95rem;
      color: var(--text-bright);
    }
    .card-tag {
      font-size: 0.7rem;
      font-weight: 700;
      padding: 2px 6px;
      border-radius: 4px;
      background: var(--purple-bg);
      color: var(--purple);
    }
    .card-meta {
      font-size: 0.78rem;
      color: var(--text-muted);
      display: flex;
      flex-direction: column;
      gap: 3px;
    }
    .card-meta a {
      color: var(--primary);
      text-decoration: none;
      display: inline-flex;
      align-items: center;
      gap: 4px;
    }
    .card-meta a:hover { text-decoration: underline; }
    
    .card-specialty {
      font-size: 0.78rem;
      background: rgba(255,255,255,0.03);
      padding: 6px 8px;
      border-radius: 6px;
      color: #D1D5DB;
      border-left: 3px solid var(--primary);
    }

    .card-finance {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding-top: 8px;
      border-top: 1px dashed var(--border-subtle);
      font-size: 0.8rem;
      font-family: 'JetBrains Mono', monospace;
    }
    .val-deal { font-weight: 700; color: #93C5FD; }
    .val-mrr {
      color: var(--success);
      font-weight: 700;
      background: var(--success-bg);
      padding: 2px 6px;
      border-radius: 4px;
    }

    .card-actions {
      display: flex;
      gap: 6px;
      margin-top: 4px;
    }
    .card-actions select {
      flex: 1;
      background: var(--bg-surface);
      color: var(--text-main);
      border: 1px solid var(--border-subtle);
      padding: 5px 8px;
      border-radius: 6px;
      font-size: 0.75rem;
      font-family: inherit;
      cursor: pointer;
    }
    .btn-zap {
      background: #22C55E;
      color: #064E3B;
      font-size: 0.75rem;
      padding: 5px 9px;
      border-radius: 6px;
      text-decoration: none;
      font-weight: 700;
      display: inline-flex;
      align-items: center;
      gap: 4px;
    }
    .btn-zap:hover { background: #16A34A; }
    .btn-upsell-trigger {
      background: var(--purple-bg);
      border: 1px solid var(--purple);
      color: #DDD6FE;
      padding: 4px 8px;
      border-radius: 6px;
      font-size: 0.72rem;
      font-weight: 700;
      cursor: pointer;
      width: 100%;
      text-align: center;
    }
    .btn-upsell-trigger:hover { background: var(--purple); color: white; }

    /* Modal */
    .modal-overlay {
      display: none;
      position: fixed;
      top: 0; left: 0; right: 0; bottom: 0;
      background: rgba(0,0,0,0.7);
      backdrop-filter: blur(4px);
      z-index: 100;
      align-items: center;
      justify-content: center;
      padding: 16px;
    }
    .modal {
      background: var(--bg-surface);
      border: 1px solid var(--border-subtle);
      border-radius: var(--radius);
      width: 100%;
      max-width: 520px;
      padding: 24px;
      display: flex;
      flex-direction: column;
      gap: 16px;
      box-shadow: 0 20px 40px rgba(0,0,0,0.6);
    }
    .modal-title {
      font-size: 1.15rem;
      font-weight: 800;
    }
    .form-group {
      display: flex;
      flex-direction: column;
      gap: 6px;
    }
    .form-group label {
      font-size: 0.8rem;
      font-weight: 600;
      color: var(--text-muted);
    }
    .form-group input, .form-group textarea, .form-group select {
      background: var(--bg-card);
      border: 1px solid var(--border-subtle);
      color: var(--text-main);
      padding: 9px 12px;
      border-radius: 6px;
      font-size: 0.88rem;
      font-family: inherit;
    }
    .form-group input:focus, .form-group textarea:focus {
      outline: none;
      border-color: var(--primary);
    }
    .modal-actions {
      display: flex;
      justify-content: flex-end;
      gap: 10px;
      margin-top: 8px;
    }

    /* Dots */
    .dot-blue { background: #3B82F6; }
    .dot-indigo { background: #6366F1; }
    .dot-amber { background: #F59E0B; }
    .dot-orange { background: #F97316; }
    .dot-green { background: #10B981; }
    .dot-cyan { background: #06B6D4; }
    .dot-purple { background: #8B5CF6; }
  </style>
</head>
<body>

  <!-- Top Header -->
  <header>
    <div class="brand">
      <div class="brand-icon">🦁</div>
      <div>
        <div class="brand-title">KONIG Pipeline CRM</div>
        <div class="brand-sub">Vendas, Hospedagem & Radar de MRR (Confeitarias Gourmet)</div>
      </div>
    </div>
    <div>
      <button class="btn btn-primary" onclick="openNewLeadModal()">+ Novo Lead</button>
      <button class="btn btn-outline" onclick="loadAllData()">🔄 Atualizar</button>
    </div>
  </header>

  <!-- Metrics Bar -->
  <div class="metrics-bar" id="metricsBar">
    <div class="metric-card">
      <div class="metric-label">Caixa Front-end (R$ 699)</div>
      <div class="metric-value val-blue" id="wonRevenue">R$ 0,00</div>
      <div class="metric-sub" id="wonCount">0 negócios fechados</div>
    </div>
    <div class="metric-card">
      <div class="metric-label">MRR de Hospedagem (Mensal)</div>
      <div class="metric-value val-green" id="totalMrr">R$ 0,00/mês</div>
      <div class="metric-sub" id="activeHosts">0 clientes pagando hospedagem</div>
    </div>
    <div class="metric-card">
      <div class="metric-label">ARR Recorrente Projetado</div>
      <div class="metric-value val-purple" id="projectedArr">R$ 0,00/ano</div>
      <div class="metric-sub">Previsão anual contratada</div>
    </div>
    <div class="metric-card">
      <div class="metric-label">Total de Leads em Pipeline</div>
      <div class="metric-value" id="totalLeads">0</div>
      <div class="metric-sub" id="conversionRate">Taxa de conversão: 0%</div>
    </div>
  </div>

  <!-- Kanban Columns Wrapper -->
  <div class="kanban-wrapper" id="kanbanBoard">
    <!-- 1. Prospecção -->
    <div class="kanban-column" data-stage="prospeccao">
      <div class="column-header">
        <div class="col-title-wrap">
          <div class="col-dot dot-blue"></div>
          <div class="col-title">1. Prospecção (Instagram)</div>
        </div>
        <div class="col-count" id="count-prospeccao">0</div>
      </div>
      <div class="cards-container" id="cards-prospeccao"></div>
    </div>

    <!-- 2. Contato Enviado -->
    <div class="kanban-column" data-stage="contato_enviado">
      <div class="column-header">
        <div class="col-title-wrap">
          <div class="col-dot dot-indigo"></div>
          <div class="col-title">2. Contato Enviado (Zap)</div>
        </div>
        <div class="col-count" id="count-contato_enviado">0</div>
      </div>
      <div class="cards-container" id="cards-contato_enviado"></div>
    </div>

    <!-- 3. Em Conversa / Demo -->
    <div class="kanban-column" data-stage="em_conversa">
      <div class="column-header">
        <div class="col-title-wrap">
          <div class="col-dot dot-amber"></div>
          <div class="col-title">3. Em Conversa / Demo</div>
        </div>
        <div class="col-count" id="count-em_conversa">0</div>
      </div>
      <div class="cards-container" id="cards-em_conversa"></div>
    </div>

    <!-- 4. Negociação -->
    <div class="kanban-column" data-stage="negociacao">
      <div class="column-header">
        <div class="col-title-wrap">
          <div class="col-dot dot-orange"></div>
          <div class="col-title">4. Negociação (Pix)</div>
        </div>
        <div class="col-count" id="count-negociacao">0</div>
      </div>
      <div class="cards-container" id="cards-negociacao"></div>
    </div>

    <!-- 5. Fechado & Pago -->
    <div class="kanban-column" data-stage="fechado_pago">
      <div class="column-header">
        <div class="col-title-wrap">
          <div class="col-dot dot-green"></div>
          <div class="col-title">5. Fechado & Pago (R$ 699)</div>
        </div>
        <div class="col-count" id="count-fechado_pago">0</div>
      </div>
      <div class="cards-container" id="cards-fechado_pago"></div>
    </div>

    <!-- 6. Em Setup 48h -->
    <div class="kanban-column" data-stage="setup_48h">
      <div class="column-header">
        <div class="col-title-wrap">
          <div class="col-dot dot-cyan"></div>
          <div class="col-title">6. Em Produção (48h)</div>
        </div>
        <div class="col-count" id="count-setup_48h">0</div>
      </div>
      <div class="cards-container" id="cards-setup_48h"></div>
    </div>

    <!-- 7. Radar de Upsell Jay Abraham -->
    <div class="kanban-column" data-stage="radar_upsell">
      <div class="column-header">
        <div class="col-title-wrap">
          <div class="col-dot dot-purple"></div>
          <div class="col-title">7. Radar LTV (Jay Abraham)</div>
        </div>
        <div class="col-count" id="count-radar_upsell">0</div>
      </div>
      <div class="cards-container" id="cards-radar_upsell"></div>
    </div>
  </div>

  <!-- Modal: Novo Lead -->
  <div class="modal-overlay" id="newLeadModal">
    <div class="modal">
      <div class="modal-title">Novo Lead de Confeitaria</div>
      <form id="newLeadForm" onsubmit="handleCreateLead(event)">
        <div class="form-group">
          <label>Nome da Confeitaria / Ateliê *</label>
          <input type="text" id="leadName" required placeholder="Ex: Doceria Sublime">
        </div>
        <div class="form-group">
          <label>Instagram (@)</label>
          <input type="text" id="leadInstagram" placeholder="@doceriasublime">
        </div>
        <div class="form-group">
          <label>WhatsApp (com DDD) *</label>
          <input type="text" id="leadWhatsapp" required placeholder="5511999998888">
        </div>
        <div class="form-group">
          <label>Especialidade</label>
          <input type="text" id="leadSpecialty" placeholder="Ex: Bolos artísticos para casamento">
        </div>
        <div class="form-group">
          <label>Plano de Hospedagem / MRR Previsto</label>
          <select id="leadMrr">
            <option value="59.0">R$ 59,00/mês (Hospedagem Básica + SSL)</option>
            <option value="79.0" selected>R$ 79,00/mês (Hospedagem Pro + Ajustes Cardápio)</option>
            <option value="97.0">R$ 97,00/mês (Hospedagem + Suporte Prioritário)</option>
          </select>
        </div>
        <div class="form-group">
          <label>Anotações / Dores Observadas</label>
          <textarea id="leadNotes" rows="3" placeholder="Link da bio atual, número de seguidores, dores observadas no feed..."></textarea>
        </div>
        <div class="modal-actions">
          <button type="button" class="btn btn-outline" onclick="closeNewLeadModal()">Cancelar</button>
          <button type="submit" class="btn btn-primary">Salvar no CRM</button>
        </div>
      </form>
    </div>
  </div>

  <!-- Modal: Script de Upsell (Jay Abraham) -->
  <div class="modal-overlay" id="upsellModal">
    <div class="modal">
      <div class="modal-title" id="upsellTitle">💎 Radar de LTV do Jay Abraham</div>
      <p style="font-size: 0.85rem; color: var(--text-muted);">
        Abordagem de consultoria preeminente baseada no Próximo Problema Lógico da cliente.
      </p>
      <div class="form-group">
        <label>Mensagem Sugerida para WhatsApp:</label>
        <textarea id="upsellScriptText" rows="9" readonly style="font-family: inherit; font-size: 0.85rem;"></textarea>
      </div>
      <div class="modal-actions">
        <button class="btn btn-outline" onclick="closeUpsellModal()">Fechar</button>
        <button class="btn btn-success" onclick="copyUpsellScript()">📋 Copiar Mensagem</button>
      </div>
    </div>
  </div>

  <script>
    const STAGES = [
      'prospeccao',
      'contato_enviado',
      'em_conversa',
      'negociacao',
      'fechado_pago',
      'setup_48h',
      'radar_upsell'
    ];

    const STAGE_NAMES = {
      'prospeccao': '1. Prospecção',
      'contato_enviado': '2. Contato Enviado',
      'em_conversa': '3. Em Conversa',
      'negociacao': '4. Negociação',
      'fechado_pago': '5. Fechado & Pago',
      'setup_48h': '6. Em Produção 48h',
      'radar_upsell': '7. Radar LTV'
    };

    async function loadAllData() {
      await Promise.all([loadMetrics(), loadDeals()]);
    }

    async function loadMetrics() {
      try {
        const res = await fetch('/api/metrics');
        const data = await res.json();
        
        document.getElementById('wonRevenue').innerText = 'R$ ' + data.won_revenue.toLocaleString('pt-BR', {minimumFractionDigits: 2});
        document.getElementById('wonCount').innerText = `${data.won_count} negócios fechados`;
        
        document.getElementById('totalMrr').innerText = 'R$ ' + data.total_mrr.toLocaleString('pt-BR', {minimumFractionDigits: 2}) + '/mês';
        document.getElementById('activeHosts').innerText = `${data.active_mrr_clients} hospedagens ativas no servidor`;
        
        document.getElementById('projectedArr').innerText = 'R$ ' + data.projected_arr.toLocaleString('pt-BR', {minimumFractionDigits: 2}) + '/ano';
        
        document.getElementById('totalLeads').innerText = data.total_leads;
        document.getElementById('conversionRate').innerText = `Taxa de conversão: ${data.conversion_rate}%`;
      } catch (err) {
        console.error('Erro ao carregar métricas:', err);
      }
    }

    async function loadDeals() {
      try {
        const res = await fetch('/api/deals');
        const deals = await res.json();

        // Limpa todas as colunas
        STAGES.forEach(s => {
          const container = document.getElementById(`cards-${s}`);
          if (container) container.innerHTML = '';
          const counter = document.getElementById(`count-${s}`);
          if (counter) counter.innerText = '0';
        });

        const counts = {};
        STAGES.forEach(s => counts[s] = 0);

        deals.forEach(deal => {
          const stage = deal.stage || 'prospeccao';
          if (counts[stage] !== undefined) counts[stage]++;

          const container = document.getElementById(`cards-${stage}`);
          if (container) {
            container.appendChild(createDealCardElement(deal));
          }
        });

        STAGES.forEach(s => {
          const counter = document.getElementById(`count-${s}`);
          if (counter) counter.innerText = counts[s] || 0;
        });

      } catch (err) {
        console.error('Erro ao carregar deals:', err);
      }
    }

    function createDealCardElement(deal) {
      const card = document.createElement('div');
      card.className = 'deal-card';
      
      const cleanZap = (deal.whatsapp || '').replace(/\\D/g, '');
      const zapLink = cleanZap ? `https://wa.me/${cleanZap}?text=Oi%20${encodeURIComponent(deal.name.split(' ')[0])},%20tudo%20bem?` : '#';

      let stageOptions = STAGES.map(s => {
        return `<option value="${s}" ${s === deal.stage ? 'selected' : ''}>Mover ➔ ${STAGE_NAMES[s]}</option>`;
      }).join('');

      card.innerHTML = `
        <div class="card-head">
          <div class="card-name">${escapeHtml(deal.name)}</div>
          <div class="card-tag">${escapeHtml(deal.niche || 'Gourmet')}</div>
        </div>
        
        <div class="card-meta">
          ${deal.instagram ? `<a href="https://instagram.com/${deal.instagram.replace('@','')}" target="_blank">📷 ${escapeHtml(deal.instagram)}</a>` : ''}
          ${deal.hosting_domain ? `<span>🌐 <b>${escapeHtml(deal.hosting_domain)}</b></span>` : ''}
        </div>

        ${deal.specialty ? `<div class="card-specialty">${escapeHtml(deal.specialty)}</div>` : ''}

        <div class="card-finance">
          <span class="val-deal">R$ ${deal.deal_value.toFixed(2)}</span>
          <span class="val-mrr">+ R$ ${deal.mrr_value.toFixed(2)}/mês MRR</span>
        </div>

        ${deal.notes ? `<p style="font-size: 0.73rem; color: #9CA3AF; font-style: italic;">"${escapeHtml(deal.notes)}</p>` : ''}

        ${deal.stage === 'radar_upsell' || deal.stage === 'fechado_pago' ? `
          <button class="btn-upsell-trigger" onclick="openUpsellModal(${deal.id})">💎 Radar de Upsell (Jay Abraham)</button>
        ` : ''}

        <div class="card-actions">
          <a href="${zapLink}" target="_blank" class="btn-zap">💬 WhatsApp</a>
          <select onchange="handleMoveStage(${deal.id}, this.value)">
            ${stageOptions}
          </select>
        </div>
      `;

      return card;
    }

    async function handleMoveStage(dealId, newStage) {
      try {
        const res = await fetch(`/api/deals/${dealId}/stage`, {
          method: 'PATCH',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ stage: newStage })
        });
        if (res.ok) {
          loadAllData();
        }
      } catch (err) {
        alert('Erro ao mover lead');
      }
    }

    async function handleCreateLead(e) {
      e.preventDefault();
      const payload = {
        name: document.getElementById('leadName').value,
        instagram: document.getElementById('leadInstagram').value,
        whatsapp: document.getElementById('leadWhatsapp').value,
        specialty: document.getElementById('leadSpecialty').value,
        mrr_value: parseFloat(document.getElementById('leadMrr').value),
        notes: document.getElementById('leadNotes').value,
        deal_value: 699.0
      };

      try {
        const res = await fetch('/api/deals', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        if (res.ok) {
          closeNewLeadModal();
          document.getElementById('newLeadForm').reset();
          loadAllData();
        }
      } catch (err) {
        alert('Erro ao salvar lead');
      }
    }

    async function openUpsellModal(dealId) {
      try {
        const res = await fetch(`/api/upsell-script/${dealId}`);
        const data = await res.json();
        document.getElementById('upsellTitle').innerText = `💎 Script de Upsell — ${data.name}`;
        document.getElementById('upsellScriptText').value = data.script;
        document.getElementById('upsellModal').style.display = 'flex';
      } catch (err) {
        alert('Erro ao buscar script de upsell');
      }
    }

    function closeUpsellModal() {
      document.getElementById('upsellModal').style.display = 'none';
    }

    function copyUpsellScript() {
      const textarea = document.getElementById('upsellScriptText');
      textarea.select();
      document.execCommand('copy');
      alert('Mensagem copiada! Só colar no WhatsApp da cliente.');
    }

    function openNewLeadModal() {
      document.getElementById('newLeadModal').style.display = 'flex';
    }
    function closeNewLeadModal() {
      document.getElementById('newLeadModal').style.display = 'none';
    }

    function escapeHtml(text) {
      if (!text) return '';
      const div = document.createElement('div');
      div.innerText = text;
      return div.innerHTML;
    }

    // Inicialização
    loadAllData();
  </script>
</body>
</html>
"""
    return HTMLResponse(content=html_content)


if __name__ == "__main__":
    import uvicorn
    init_db()
    uvicorn.run("crm.server:app", host="127.0.0.1", port=8000, reload=True)
