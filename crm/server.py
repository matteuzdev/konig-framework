"""
KONIG Sales, Hosting & MRR CRM — FastAPI Server & Interactive Kanban UI.

Projetado por:
- Bob (Arquitetura & APIs)
- Carol (Design System, Tokens HSL & Usabilidade Ergonômica)
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

app = FastAPI(title="KONIG Sales & MRR CRM", version="2.1.0")


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
        f"Oi {first_name}, tudo bem? Aqui é da equipe técnica do seu site.\n\n"
        f"A sua página está rodando em nosso servidor seguro há alguns dias e analisamos que várias pessoas "
        f"já acessaram o seu cardápio pelo link da bio do Instagram.\n\n"
        f"Identificamos que muitas clientes deixam para pedir bolo em cima da hora e às vezes esquecem a data da festa. "
        f"Nós criamos uma automação por IA que conecta no seu site e avisa a cliente 3 dias antes da data festiva "
        f"com um lembrete no WhatsApp para ela confirmar o pedido.\n\n"
        f"Como você já é nossa cliente na hospedagem de R$ {int(mrr)}/mês, conseguimos ativar esse módulo "
        f"de Lembrete de Encomendas por apenas R$ 47/mês a mais. Gostaria de ativar um teste em seu cardápio essa semana?"
    )
    
    return {
        "deal_id": deal_id,
        "name": name,
        "upsell_name": "Lembrete Automático de Encomendas & Festas (IA)",
        "script": script
    }


@app.get("/", response_class=HTMLResponse)
def serve_kanban_dashboard():
    """Interface visual do CRM projetada com Design Tokens profissionais, SVG icons e layout ergonômico."""
    html_content = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>KONIG CRM — Vendas, Hospedagem & MRR</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;600;700&display=swap" rel="stylesheet">
  <style>
    :root {
      /* Tema Dark Carbon (Padrão Operacional Ergonômico) */
      --bg-app: #090D14;
      --bg-surface: #0F172A;
      --bg-card: #141E33;
      --bg-card-hover: #1A2742;
      --border-subtle: #1E293B;
      --border-strong: #334155;
      --border-focus: #3B82F6;

      --text-main: #E2E8F0;
      --text-muted: #94A3B8;
      --text-dim: #64748B;
      --text-bright: #FFFFFF;

      --primary: #2563EB;
      --primary-hover: #1D4ED8;
      --success: #10B981;
      --success-bg: rgba(16, 185, 129, 0.1);
      --warning: #F59E0B;
      --warning-bg: rgba(245, 158, 11, 0.1);
      --purple: #8B5CF6;
      --purple-bg: rgba(139, 92, 246, 0.12);

      --scrollbar-thumb: rgba(148, 163, 184, 0.22);
      --scrollbar-thumb-hover: rgba(148, 163, 184, 0.45);
      --shadow-card: 0 1px 3px rgba(0, 0, 0, 0.25);
      --radius-sm: 6px;
      --radius: 8px;
    }

    [data-theme="light"] {
      /* Tema Light Studio (Clareza Executiva) */
      --bg-app: #F8FAFC;
      --bg-surface: #FFFFFF;
      --bg-card: #FFFFFF;
      --bg-card-hover: #F1F5F9;
      --border-subtle: #E2E8F0;
      --border-strong: #CBD5E1;
      --border-focus: #2563EB;

      --text-main: #334155;
      --text-muted: #64748B;
      --text-dim: #94A3B8;
      --text-bright: #0F172A;

      --primary: #2563EB;
      --primary-hover: #1D4ED8;
      --success: #059669;
      --success-bg: rgba(5, 150, 105, 0.08);
      --warning: #D97706;
      --warning-bg: rgba(217, 119, 6, 0.08);
      --purple: #7C3AED;
      --purple-bg: rgba(124, 58, 237, 0.08);

      --scrollbar-thumb: rgba(100, 116, 139, 0.2);
      --scrollbar-thumb-hover: rgba(100, 116, 139, 0.4);
      --shadow-card: 0 1px 3px rgba(0, 0, 0, 0.05);
    }

    /* Reset Ergonômico de 100vh: Sem scrolls globais desnecessários */
    * {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
      scrollbar-width: thin;
      scrollbar-color: var(--scrollbar-thumb) transparent;
    }

    html, body {
      height: 100vh;
      max-height: 100vh;
      overflow: hidden;
      font-family: 'Plus Jakarta Sans', -apple-system, sans-serif;
      background-color: var(--bg-app);
      color: var(--text-main);
      display: flex;
      flex-direction: column;
      -webkit-font-smoothing: antialiased;
    }

    /* Scrollbars Modernas e Discretas (Elimina barras cinzas dos anos 90) */
    ::-webkit-scrollbar {
      width: 5px;
      height: 5px;
    }
    ::-webkit-scrollbar-track {
      background: transparent;
    }
    ::-webkit-scrollbar-thumb {
      background: var(--scrollbar-thumb);
      border-radius: 999px;
    }
    ::-webkit-scrollbar-thumb:hover {
      background: var(--scrollbar-thumb-hover);
    }
    ::-webkit-scrollbar-button {
      display: none;
      width: 0;
      height: 0;
    }

    /* Header Compacto de Controle */
    header {
      background: var(--bg-surface);
      border-bottom: 1px solid var(--border-subtle);
      height: 56px;
      min-height: 56px;
      padding: 0 20px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      z-index: 30;
    }

    .brand {
      display: flex;
      align-items: center;
      gap: 12px;
    }

    .brand-mark {
      width: 32px;
      height: 32px;
      background: var(--primary);
      border-radius: var(--radius-sm);
      display: flex;
      align-items: center;
      justify-content: center;
      color: #FFFFFF;
    }

    .brand-info {
      display: flex;
      flex-direction: column;
    }

    .brand-title {
      font-weight: 700;
      font-size: 0.95rem;
      letter-spacing: -0.01em;
      color: var(--text-bright);
      line-height: 1.2;
    }

    .brand-sub {
      font-size: 0.72rem;
      color: var(--text-muted);
      letter-spacing: 0.02em;
    }

    .header-controls {
      display: flex;
      align-items: center;
      gap: 8px;
    }

    .btn {
      height: 34px;
      padding: 0 14px;
      border-radius: var(--radius-sm);
      font-weight: 600;
      font-size: 0.8rem;
      cursor: pointer;
      border: 1px solid transparent;
      display: inline-flex;
      align-items: center;
      gap: 6px;
      font-family: inherit;
      transition: all 0.15s ease;
    }

    .btn-primary {
      background: var(--primary);
      color: #FFFFFF;
    }
    .btn-primary:hover {
      background: var(--primary-hover);
    }

    .btn-outline {
      background: transparent;
      border-color: var(--border-subtle);
      color: var(--text-main);
    }
    .btn-outline:hover {
      background: var(--bg-card-hover);
      border-color: var(--border-strong);
    }

    .btn-icon {
      width: 34px;
      height: 34px;
      padding: 0;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      border-radius: var(--radius-sm);
      border: 1px solid var(--border-subtle);
      background: transparent;
      color: var(--text-muted);
      cursor: pointer;
      transition: all 0.15s ease;
    }
    .btn-icon:hover {
      color: var(--text-bright);
      border-color: var(--border-strong);
      background: var(--bg-card-hover);
    }

    /* Barra Superior de Métricas Executivas */
    .metrics-bar {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 12px;
      padding: 12px 20px 8px;
      background: var(--bg-app);
    }

    .metric-card {
      background: var(--bg-surface);
      border: 1px solid var(--border-subtle);
      border-radius: var(--radius);
      padding: 10px 14px;
      display: flex;
      flex-direction: column;
      gap: 2px;
      box-shadow: var(--shadow-card);
    }

    .metric-label {
      font-size: 0.7rem;
      font-weight: 600;
      color: var(--text-muted);
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }

    .metric-value {
      font-size: 1.35rem;
      font-weight: 700;
      font-family: 'JetBrains Mono', monospace;
      letter-spacing: -0.02em;
      line-height: 1.2;
    }

    .metric-sub {
      font-size: 0.72rem;
      color: var(--text-dim);
    }

    .val-blue { color: var(--primary); }
    .val-green { color: var(--success); }
    .val-purple { color: var(--purple); }

    /* Tabuleiro Kanban Flexível (Zero scroll vertical global) */
    .board-container {
      flex: 1;
      min-height: 0;
      padding: 8px 20px 14px;
      display: flex;
      flex-direction: column;
    }

    .kanban-wrapper {
      flex: 1;
      min-height: 0;
      display: flex;
      gap: 12px;
      overflow-x: auto;
      overflow-y: hidden;
      padding-bottom: 6px;
    }

    .kanban-column {
      background: var(--bg-surface);
      border: 1px solid var(--border-subtle);
      border-radius: var(--radius);
      width: 295px;
      min-width: 295px;
      max-width: 295px;
      display: flex;
      flex-direction: column;
      height: 100%;
      min-height: 0;
    }

    .column-header {
      padding: 10px 14px;
      border-bottom: 1px solid var(--border-subtle);
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 8px;
      background: rgba(255, 255, 255, 0.015);
      border-top-left-radius: var(--radius);
      border-top-right-radius: var(--radius);
    }

    .col-title-wrap {
      display: flex;
      align-items: center;
      gap: 8px;
      min-width: 0;
      flex: 1;
    }

    .col-dot {
      width: 8px;
      height: 8px;
      min-width: 8px;
      border-radius: 50%;
    }

    .col-title {
      font-weight: 700;
      font-size: 0.8rem;
      letter-spacing: -0.01em;
      color: var(--text-bright);
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    .col-count {
      background: var(--bg-app);
      border: 1px solid var(--border-subtle);
      font-size: 0.7rem;
      font-weight: 700;
      padding: 1px 7px;
      border-radius: 12px;
      color: var(--text-muted);
      font-family: 'JetBrains Mono', monospace;
      flex-shrink: 0;
    }

    .cards-container {
      padding: 10px;
      overflow-y: auto;
      overflow-x: hidden;
      display: flex;
      flex-direction: column;
      gap: 10px;
      flex: 1;
      min-height: 0;
    }

    /* Cards do Pipeline */
    .deal-card {
      background: var(--bg-card);
      border: 1px solid var(--border-subtle);
      border-radius: var(--radius-sm);
      padding: 12px;
      display: flex;
      flex-direction: column;
      gap: 8px;
      box-shadow: var(--shadow-card);
      transition: border-color 0.15s ease, background-color 0.15s ease;
      overflow: hidden;
    }

    .deal-card:hover {
      border-color: var(--border-strong);
      background: var(--bg-card-hover);
    }

    .card-head {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      gap: 6px;
    }

    .card-name {
      font-weight: 700;
      font-size: 0.88rem;
      color: var(--text-bright);
      line-height: 1.25;
    }

    .card-tag {
      font-size: 0.68rem;
      font-weight: 700;
      padding: 2px 6px;
      border-radius: 4px;
      background: var(--purple-bg);
      color: var(--purple);
      white-space: nowrap;
    }

    .card-meta {
      font-size: 0.74rem;
      color: var(--text-muted);
      display: flex;
      flex-direction: column;
      gap: 3px;
    }

    .card-meta a, .card-meta span {
      color: var(--text-muted);
      text-decoration: none;
      display: inline-flex;
      align-items: center;
      gap: 5px;
    }
    .card-meta a:hover {
      color: var(--primary);
    }

    .card-specialty {
      font-size: 0.73rem;
      background: rgba(255, 255, 255, 0.025);
      padding: 5px 8px;
      border-radius: 4px;
      color: var(--text-muted);
      border-left: 2px solid var(--primary);
    }

    .card-finance {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding-top: 6px;
      border-top: 1px dashed var(--border-subtle);
      font-size: 0.76rem;
      font-family: 'JetBrains Mono', monospace;
    }

    .val-deal {
      font-weight: 700;
      color: var(--primary);
    }

    .val-mrr {
      color: var(--success);
      font-weight: 700;
      background: var(--success-bg);
      padding: 1px 5px;
      border-radius: 3px;
    }

    .card-notes {
      font-size: 0.71rem;
      color: var(--text-dim);
      font-style: italic;
      line-height: 1.3;
    }

    .btn-upsell-trigger {
      background: var(--purple-bg);
      border: 1px solid var(--purple);
      color: var(--purple);
      padding: 5px 8px;
      border-radius: var(--radius-sm);
      font-size: 0.72rem;
      font-weight: 600;
      cursor: pointer;
      width: 100%;
      text-align: center;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 6px;
      transition: all 0.15s ease;
    }
    .btn-upsell-trigger:hover {
      background: var(--purple);
      color: #FFFFFF;
    }

    .card-actions {
      display: flex;
      gap: 6px;
      margin-top: 2px;
    }

    .btn-zap {
      background: #10B981;
      color: #FFFFFF;
      font-size: 0.72rem;
      padding: 4px 8px;
      border-radius: var(--radius-sm);
      text-decoration: none;
      font-weight: 600;
      display: inline-flex;
      align-items: center;
      gap: 4px;
      white-space: nowrap;
      transition: opacity 0.15s ease;
    }
    .btn-zap:hover { opacity: 0.9; }

    .card-actions select {
      flex: 1;
      min-width: 0;
      background: var(--bg-surface);
      color: var(--text-main);
      border: 1px solid var(--border-subtle);
      padding: 4px 6px;
      border-radius: var(--radius-sm);
      font-size: 0.72rem;
      font-family: inherit;
      cursor: pointer;
    }
    .card-actions select:focus {
      outline: none;
      border-color: var(--border-focus);
    }

    /* Modais */
    .modal-overlay {
      display: none;
      position: fixed;
      top: 0; left: 0; right: 0; bottom: 0;
      background: rgba(0, 0, 0, 0.65);
      backdrop-filter: blur(4px);
      z-index: 100;
      align-items: center;
      justify-content: center;
      padding: 16px;
    }

    .modal {
      background: var(--bg-surface);
      border: 1px solid var(--border-strong);
      border-radius: var(--radius);
      width: 100%;
      max-width: 480px;
      padding: 22px;
      box-shadow: 0 16px 36px rgba(0, 0, 0, 0.4);
      display: flex;
      flex-direction: column;
      gap: 16px;
    }

    .modal-title {
      font-size: 1.05rem;
      font-weight: 700;
      color: var(--text-bright);
      letter-spacing: -0.01em;
    }

    .modal-subtitle {
      font-size: 0.76rem;
      color: var(--text-muted);
      line-height: 1.4;
      margin-top: -10px;
    }

    .form-group {
      display: flex;
      flex-direction: column;
      gap: 5px;
    }

    .form-group label {
      font-size: 0.74rem;
      font-weight: 600;
      color: var(--text-muted);
      text-transform: uppercase;
      letter-spacing: 0.04em;
    }

    .form-group input, .form-group select, .form-group textarea {
      background: var(--bg-app);
      border: 1px solid var(--border-subtle);
      color: var(--text-bright);
      border-radius: var(--radius-sm);
      padding: 8px 10px;
      font-size: 0.82rem;
      font-family: inherit;
      outline: none;
      transition: border-color 0.15s ease;
    }
    .form-group input:focus, .form-group select:focus, .form-group textarea:focus {
      border-color: var(--border-focus);
    }

    .modal-actions {
      display: flex;
      justify-content: flex-end;
      gap: 8px;
      padding-top: 6px;
    }

    /* Cores dos Dots dos Estágios */
    .dot-blue { background: #3B82F6; }
    .dot-indigo { background: #6366F1; }
    .dot-amber { background: #F59E0B; }
    .dot-orange { background: #F97316; }
    .dot-green { background: #10B981; }
    .dot-cyan { background: #06B6D4; }
    .dot-purple { background: #8B5CF6; }
    .dot-gray { background: #64748B; }
  </style>
</head>
<body>

  <!-- Top Header de Controle -->
  <header>
    <div class="brand">
      <div class="brand-mark">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round">
          <polygon points="12 2 2 7 12 12 22 7 12 2"></polygon>
          <polyline points="2 17 12 22 22 17"></polyline>
          <polyline points="2 12 12 17 22 12"></polyline>
        </svg>
      </div>
      <div class="brand-info">
        <div class="brand-title">KONIG Pipeline CRM</div>
        <div class="brand-sub">Gestão de Vendas, Hospedagem & Radar LTV (Jay Abraham)</div>
      </div>
    </div>
    <div class="header-controls">
      <button class="btn btn-primary" onclick="openNewLeadModal()">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round">
          <line x1="12" y1="5" x2="12" y2="19"></line>
          <line x1="5" y1="12" x2="19" y2="12"></line>
        </svg>
        Novo Lead
      </button>
      <button class="btn btn-outline" onclick="loadAllData()">
        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <polyline points="23 4 23 10 17 10"></polyline>
          <polyline points="1 20 1 14 7 14"></polyline>
          <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path>
        </svg>
        Atualizar
      </button>
      <button class="btn-icon" id="themeToggleBtn" onclick="toggleTheme()" title="Alternar Modo Escuro / Claro">
        <svg id="themeIcon" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="12" cy="12" r="5"></circle>
          <line x1="12" y1="1" x2="12" y2="3"></line>
          <line x1="12" y1="21" x2="12" y2="23"></line>
          <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line>
          <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line>
          <line x1="1" y1="12" x2="3" y2="12"></line>
          <line x1="21" y1="12" x2="23" y2="12"></line>
          <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line>
          <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line>
        </svg>
      </button>
    </div>
  </header>

  <!-- Barra de Métricas Financeiras -->
  <div class="metrics-bar" id="metricsBar">
    <div class="metric-card">
      <div class="metric-label">Caixa Front-End (R$ 699)</div>
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

  <!-- Tabuleiro Kanban Ergonômico -->
  <div class="board-container">
    <div class="kanban-wrapper" id="kanbanBoard">
      <!-- 1. Prospecção -->
      <div class="kanban-column" data-stage="prospeccao">
        <div class="column-header">
          <div class="col-title-wrap">
            <div class="col-dot dot-blue"></div>
            <div class="col-title">1. Prospecção</div>
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
            <div class="col-title">2. Primeiro Contato</div>
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
            <div class="col-title">3. Em Qualificação</div>
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
            <div class="col-title">5. Fechado & Pago</div>
          </div>
          <div class="col-count" id="count-fechado_pago">0</div>
        </div>
        <div class="cards-container" id="cards-fechado_pago"></div>
      </div>

      <!-- 6. Em Produção -->
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

      <!-- 7. No Ar & MRR Ativo -->
      <div class="kanban-column" data-stage="radar_upsell">
        <div class="column-header">
          <div class="col-title-wrap">
            <div class="col-dot dot-purple"></div>
            <div class="col-title">7. No Ar & MRR Ativo</div>
          </div>
          <div class="col-count" id="count-radar_upsell">0</div>
        </div>
        <div class="cards-container" id="cards-radar_upsell"></div>
      </div>

      <!-- 8. Perdido -->
      <div class="kanban-column" data-stage="perdido">
        <div class="column-header">
          <div class="col-title-wrap">
            <div class="col-dot dot-gray"></div>
            <div class="col-title">8. Desqualificado</div>
          </div>
          <div class="col-count" id="count-perdido">0</div>
        </div>
        <div class="cards-container" id="cards-perdido"></div>
      </div>
    </div>
  </div>

  <!-- Modal: Novo Lead -->
  <div class="modal-overlay" id="newLeadModal">
    <div class="modal">
      <div class="modal-title">Cadastrar Lead de Confeitaria</div>
      <form id="newLeadForm" onsubmit="handleCreateLead(event)">
        <div class="form-group">
          <label>Nome do Estabelecimento *</label>
          <input type="text" id="leadName" required placeholder="Ex: Ateliê Sandra Bolos">
        </div>
        <div class="form-group">
          <label>Perfil do Instagram</label>
          <input type="text" id="leadInstagram" placeholder="@ateliesandra">
        </div>
        <div class="form-group">
          <label>WhatsApp (com DDD) *</label>
          <input type="text" id="leadWhatsapp" required placeholder="5511999998888">
        </div>
        <div class="form-group">
          <label>Especialidade</label>
          <input type="text" id="leadSpecialty" placeholder="Ex: Bolos artísticos, bentô cakes">
        </div>
        <div class="form-group">
          <label>Plano de Hospedagem / MRR Previsto</label>
          <select id="leadMrr">
            <option value="59.0">R$ 59,00/mês (Hospedagem Gerenciada + SSL)</option>
            <option value="79.0" selected>R$ 79,00/mês (Hospedagem Pro + Ajustes de Cardápio)</option>
            <option value="97.0">R$ 97,00/mês (Hospedagem + Suporte Prioritário)</option>
          </select>
        </div>
        <div class="form-group">
          <label>Anotações do Perfil</label>
          <textarea id="leadNotes" rows="2" placeholder="Link da bio atual, seguidores, dores observadas no atendimento..."></textarea>
        </div>
        <div class="modal-actions">
          <button type="button" class="btn btn-outline" onclick="closeNewLeadModal()">Cancelar</button>
          <button type="submit" class="btn btn-primary">Salvar Lead</button>
        </div>
      </form>
    </div>
  </div>

  <!-- Modal: Roteiro de Upsell (Jay Abraham) -->
  <div class="modal-overlay" id="upsellModal">
    <div class="modal">
      <div class="modal-title" id="upsellTitle">Estratégia de Expansão de Conta</div>
      <div class="modal-subtitle">Abordagem de consultoria baseada na heurística do Próximo Problema Lógico do cliente.</div>
      <div class="form-group">
        <label>Mensagem para WhatsApp</label>
        <textarea id="upsellScriptText" rows="7" readonly style="font-family: inherit; font-size: 0.8rem; line-height: 1.45;"></textarea>
      </div>
      <div class="modal-actions">
        <button type="button" class="btn btn-outline" onclick="closeUpsellModal()">Fechar</button>
        <button type="button" class="btn btn-primary" onclick="copyUpsellScript()">
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
            <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
          </svg>
          Copiar Mensagem
        </button>
      </div>
    </div>
  </div>

  <!-- Scripts do CRM -->
  <script>
    const STAGES = [
      'prospeccao',
      'contato_enviado',
      'em_conversa',
      'negociacao',
      'fechado_pago',
      'setup_48h',
      'radar_upsell',
      'perdido'
    ];

    const STAGE_NAMES = {
      'prospeccao': '1. Prospecção',
      'contato_enviado': '2. Primeiro Contato',
      'em_conversa': '3. Em Qualificação',
      'negociacao': '4. Negociação (Pix)',
      'fechado_pago': '5. Fechado & Pago',
      'setup_48h': '6. Em Produção (48h)',
      'radar_upsell': '7. No Ar & MRR Ativo',
      'perdido': '8. Desqualificado'
    };

    // Gerenciador de Tema (Dark / Light) com persistência
    function applyTheme(theme) {
      if (theme === 'light') {
        document.documentElement.setAttribute('data-theme', 'light');
        document.getElementById('themeIcon').innerHTML = `
          <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>
        `;
      } else {
        document.documentElement.removeAttribute('data-theme');
        document.getElementById('themeIcon').innerHTML = `
          <circle cx="12" cy="12" r="5"></circle>
          <line x1="12" y1="1" x2="12" y2="3"></line>
          <line x1="12" y1="21" x2="12" y2="23"></line>
          <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line>
          <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line>
          <line x1="1" y1="12" x2="3" y2="12"></line>
          <line x1="21" y1="12" x2="23" y2="12"></line>
          <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line>
          <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line>
        `;
      }
      localStorage.setItem('konig_crm_theme', theme);
    }

    function toggleTheme() {
      const current = document.documentElement.getAttribute('data-theme') === 'light' ? 'light' : 'dark';
      applyTheme(current === 'light' ? 'dark' : 'light');
    }

    // Inicializa tema salvo
    const savedTheme = localStorage.getItem('konig_crm_theme') || 'dark';
    applyTheme(savedTheme);

    // Rolagem horizontal ergonômica com a roda do mouse sobre o tabuleiro
    const board = document.getElementById('kanbanBoard');
    board.addEventListener('wheel', (e) => {
      if (e.deltaY !== 0 && !e.target.closest('.cards-container')) {
        board.scrollLeft += e.deltaY;
        e.preventDefault();
      }
    }, { passive: false });

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
        console.error('Erro ao carregar leads:', err);
      }
    }

    function createDealCardElement(deal) {
      const card = document.createElement('div');
      card.className = 'deal-card';
      
      const cleanZap = (deal.whatsapp || '').replace(/\\D/g, '');
      const zapLink = cleanZap ? `https://wa.me/${cleanZap}?text=Olá%20${encodeURIComponent(deal.name.split(' ')[0])},%20tudo%20bem?` : '#';

      let stageOptions = STAGES.map(s => {
        return `<option value="${s}" ${s === deal.stage ? 'selected' : ''}>${STAGE_NAMES[s]}</option>`;
      }).join('');

      card.innerHTML = `
        <div class="card-head">
          <div class="card-name">${escapeHtml(deal.name)}</div>
          <div class="card-tag">${escapeHtml(deal.niche || 'Gourmet')}</div>
        </div>
        
        <div class="card-meta">
          ${deal.instagram ? `
            <a href="https://instagram.com/${deal.instagram.replace('@','')}" target="_blank">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <rect x="2" y="2" width="20" height="20" rx="5" ry="5"></rect>
                <path d="M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37z"></path>
                <line x1="17.5" y1="6.5" x2="17.51" y2="6.5"></line>
              </svg>
              ${escapeHtml(deal.instagram)}
            </a>` : ''}
          ${deal.hosting_domain ? `
            <span>
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="10"></circle>
                <line x1="2" y1="12" x2="22" y2="12"></line>
                <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"></path>
              </svg>
              <b>${escapeHtml(deal.hosting_domain)}</b>
            </span>` : ''}
        </div>

        ${deal.specialty ? `<div class="card-specialty">${escapeHtml(deal.specialty)}</div>` : ''}

        <div class="card-finance">
          <span class="val-deal">R$ ${deal.deal_value.toFixed(2)}</span>
          <span class="val-mrr">+ R$ ${deal.mrr_value.toFixed(2)}/mês MRR</span>
        </div>

        ${deal.notes ? `<div class="card-notes">"${escapeHtml(deal.notes)}"</div>` : ''}

        ${deal.stage === 'radar_upsell' || deal.stage === 'fechado_pago' ? `
          <button class="btn-upsell-trigger" onclick="openUpsellModal(${deal.id})">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
              <polyline points="23 6 13.5 15.5 8.5 10.5 1 18"></polyline>
              <polyline points="17 6 23 6 23 12"></polyline>
            </svg>
            Radar de Expansão (LTV)
          </button>
        ` : ''}

        <div class="card-actions">
          <a href="${zapLink}" target="_blank" class="btn-zap">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"></path>
            </svg>
            WhatsApp
          </a>
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
        document.getElementById('upsellTitle').innerText = `Estratégia de Expansão — ${data.name}`;
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
      alert('Mensagem copiada para a área de transferência.');
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
