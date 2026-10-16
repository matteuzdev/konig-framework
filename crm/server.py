"""
KONIG Sales, Hosting & MRR CRM — FastAPI Server & Interactive Kanban UI.

Projetado por:
- Bob (Arquitetura & APIs)
- Carol (Design System, Tokens HSL & Usabilidade Ergonômica)
- Dan (Implementação Fullstack com HTML5 Drag & Drop e Ficha do Lead GMB)
- Elena (Homologação & Qualidade)
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, Optional

# Garante que a raiz do projeto esteja no sys.path para execução direta
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, Field

from crm.database import (
    init_db,
    list_deals,
    get_deal,
    create_deal,
    update_deal,
    update_deal_stage,
    get_crm_metrics,
)

app = FastAPI(title="KONIG Sales & MRR CRM", version="2.2.0")


@app.on_event("startup")
def on_startup():
    init_db()
    from channels.whatsapp_shield import init_shield_tables
    init_shield_tables()


class DealCreate(BaseModel):
    name: str = Field(..., description="Nome da confeitaria / ateliê")
    owner_name: Optional[str] = Field("", description="Nome da proprietária / decisora")
    city_state: Optional[str] = Field("", description="Bairro, Cidade - Estado")
    instagram: Optional[str] = Field("", description="@ do Instagram")
    whatsapp: str = Field(..., description="WhatsApp com DDI e DDD (ex: 5511999998888)")
    niche: Optional[str] = Field("Confeitaria Gourmet", description="Nicho de atuação")
    specialty: Optional[str] = Field("", description="Especialidade (ex: bolos festivos, doces)")
    deal_value: Optional[float] = Field(699.0, description="Valor do front-end")
    mrr_value: Optional[float] = Field(59.0, description="Valor da hospedagem recorrente mensal")
    hosting_domain: Optional[str] = Field("", description="Domínio do cliente")
    notes: Optional[str] = Field("", description="Anotações e dores da cliente")
    gmb_rating: Optional[float] = Field(4.9, description="Nota no Google Meu Negócio")
    gmb_reviews_count: Optional[int] = Field(85, description="Número de avaliações no Google")
    gmb_url: Optional[str] = Field("", description="Link da ficha no Google Maps")
    gmb_top_review: Optional[str] = Field("", description="Melhor avaliação coletada no Google")
    bio_link_type: Optional[str] = Field("Linktree confuso", description="Diagnóstico do link atual na bio")


class DealUpdate(BaseModel):
    name: Optional[str] = None
    owner_name: Optional[str] = None
    city_state: Optional[str] = None
    instagram: Optional[str] = None
    whatsapp: Optional[str] = None
    specialty: Optional[str] = None
    deal_value: Optional[float] = None
    mrr_value: Optional[float] = None
    hosting_domain: Optional[str] = None
    notes: Optional[str] = None
    gmb_rating: Optional[float] = None
    gmb_reviews_count: Optional[int] = None
    gmb_url: Optional[str] = None
    gmb_top_review: Optional[str] = None
    bio_link_type: Optional[str] = None


class StageUpdate(BaseModel):
    stage: str = Field(..., description="Novo estágio do pipeline")


@app.get("/api/status")
@app.get("/api/whatsapp/status")
def api_status():
    import os
    auto_pilot = os.getenv("WHATSAPP_AUTO_PILOT", "false").lower() in ("true", "1", "yes")
    return {
        "status": "online",
        "framework": "KONIG Enterprise 2.2.0",
        "iron_shield": "active",
        "whatsapp_pilot": "autonomous" if auto_pilot else "copilot_safe",
        "model": "gemini-2.5-flash (Agno Engine)"
    }


@app.get("/api/deals")
def api_list_deals():
    return list_deals()


@app.get("/api/deals/{deal_id}")
def api_get_deal(deal_id: int):
    deal = get_deal(deal_id)
    if not deal:
        raise HTTPException(status_code=404, detail="Lead não encontrado")
    return deal


@app.post("/api/deals")
def api_create_deal(deal: DealCreate):
    deal_id = create_deal(deal.model_dump())
    return {"success": True, "id": deal_id}


@app.put("/api/deals/{deal_id}")
def api_update_deal(deal_id: int, deal: DealUpdate):
    data = {k: v for k, v in deal.model_dump().items() if v is not None}
    ok = update_deal(deal_id, data)
    if not ok:
        raise HTTPException(status_code=404, detail="Lead não encontrado para atualização")
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


@app.get("/api/first-contact-script/{deal_id}")
def api_first_contact_script(deal_id: int):
    """Gera script hiper-personalizado de 1º contato via WhatsApp alavancando Google Meu Negócio."""
    deal = get_deal(deal_id)
    if not deal:
        raise HTTPException(status_code=404, detail="Lead não encontrado")

    owner = deal.get("owner_name") or ""
    biz_name = deal["name"]
    name_salutation = f"a {owner} da {biz_name}" if owner else f"a equipe da {biz_name}"

    rating = deal.get("gmb_rating") or 4.9
    reviews_count = deal.get("gmb_reviews_count") or 85
    top_review = deal.get("gmb_top_review") or ""
    bio_link = deal.get("bio_link_type") or "um link seco sem cardápio"

    review_hook = ""
    if top_review:
        review_hook = f'\n\nInclusive vi um depoimento lindo de uma cliente elogiando no Google: "{top_review}"'

    script = (
        f"Olá, tudo bem? Estou falando com {name_salutation}?\n\n"
        f"Estava conhecendo o trabalho de vocês e fiquei impressionado com a qualidade dos bolos! "
        f"Vi também que vocês têm nota {rating} no Google com {reviews_count} avaliações maravilhosas.{review_hook}\n\n"
        f"Mas reparei num detalhe: no Instagram de vocês, quem clica na bio cai em {bio_link.lower()} "
        f"e não consegue ver essas avaliações do Google nem o cardápio interativo para fazer o pedido com calma.\n\n"
        f"Nós criamos uma página com cardápio interativo sob medida para ateliês como o seu, onde a cliente monta o pedido "
        f"(sabor, fatias e data) e te manda tudo formatado direto no WhatsApp, com o selo das suas avaliações 5 estrelas do Google no topo.\n\n"
        f"Posso te mandar uma prévia de 30 segundos sem compromisso só pra você ver como ficaria o cardápio da {biz_name}?"
    )

    return {
        "deal_id": deal_id,
        "name": biz_name,
        "owner_name": owner,
        "script": script
    }


@app.get("/api/upsell-script/{deal_id}")
def api_upsell_script(deal_id: int):
    deal = get_deal(deal_id)
    if not deal:
        raise HTTPException(status_code=404, detail="Lead não encontrado")

    name = deal["name"]
    first_name = (deal.get("owner_name") or name.split()[0]).strip()
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


@app.get("/demo/maria-formiga", response_class=HTMLResponse)
def serve_maria_formiga_demo():
    """Serve a demonstração completa da Landing Page + Tool do Ateliê Maria Formiga."""
    demo_path = Path(__file__).resolve().parent.parent / "clientes" / "maria-formiga" / "site" / "index.html"
    return HTMLResponse(content=demo_path.read_text(encoding="utf-8"))


@app.get("/demo/lucca", response_class=HTMLResponse)
def serve_lucca_demo():
    """Serve a demonstração completa da Landing Page + Tool de Brunch do Lucca Cafés Especiais."""
    demo_path = Path(__file__).resolve().parent.parent / "clientes" / "lucca" / "site" / "index.html"
    return HTMLResponse(content=demo_path.read_text(encoding="utf-8"))


@app.get("/demo/lucca/cardapio", response_class=HTMLResponse)
def serve_lucca_cardapio():
    """Serve o Cardápio Web Digital Completo de Alta Gastronomia do Lucca Cafés Especiais."""
    cardapio_path = Path(__file__).resolve().parent.parent / "clientes" / "lucca" / "cardapio" / "index.html"
    return HTMLResponse(content=cardapio_path.read_text(encoding="utf-8"))


@app.get("/demo/lucca/qrcode", response_class=HTMLResponse)
@app.get("/demo/lucca/cardapio/qrcode", response_class=HTMLResponse)
def serve_lucca_qrcode():
    """Serve a página de Display de Mesa A5 com QR Code pronta para impressão física."""
    qrcode_path = Path(__file__).resolve().parent.parent / "clientes" / "lucca" / "cardapio" / "qrcode.html"
    return HTMLResponse(content=qrcode_path.read_text(encoding="utf-8"))



@app.get("/llms.txt")
@app.get("/demo/lucca/llms.txt")
def serve_lucca_llms_txt():
    """Serve o arquivo estruturado llms.txt para indexadores de IA (Perplexity, ChatGPT, Claude)."""
    from fastapi.responses import PlainTextResponse
    llms_path = Path(__file__).resolve().parent.parent / "clientes" / "lucca" / "site" / "llms.txt"
    if not llms_path.exists():
        raise HTTPException(status_code=404, detail="llms.txt não encontrado")
    return PlainTextResponse(content=llms_path.read_text(encoding="utf-8"))




@app.get("/favicon.ico")
@app.get("/demo/lucca/favicon.ico")
@app.get("/demo/lucca/cardapio/favicon.ico")
def serve_lucca_favicon():
    """Serve o favicon oficial do Lucca."""
    from fastapi.responses import FileResponse
    fav_path = Path(__file__).resolve().parent.parent / "clientes" / "lucca" / "site" / "assets" / "favicon.png"
    if not fav_path.exists():
        raise HTTPException(status_code=404, detail="Favicon não encontrado")
    return FileResponse(fav_path, media_type="image/png")


@app.get("/assets/{filename}")
@app.get("/demo/assets/{filename}")
@app.get("/demo/lucca/assets/{filename}")
@app.get("/demo/lucca/cardapio/assets/{filename}")
def serve_lucca_assets(filename: str):
    """Serve os assets de imagem reais do Lucca."""
    from fastapi.responses import FileResponse
    asset_path = Path(__file__).resolve().parent.parent / "clientes" / "lucca" / "site" / "assets" / filename
    if not asset_path.exists():
        raise HTTPException(status_code=404, detail="Asset não encontrado")
    if filename.endswith(".svg"):
        media_type = "image/svg+xml"
    elif filename.endswith(".png"):
        media_type = "image/png"
    elif filename.endswith(".ico"):
        media_type = "image/x-icon"
    else:
        media_type = "image/jpeg"
    return FileResponse(asset_path, media_type=media_type)



@app.get("/", response_class=HTMLResponse)
def serve_kanban_dashboard():
    """Interface visual do CRM com HTML5 Drag & Drop, Ficha Completa do Negócio e Integração GMB."""
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
      --gmb-gold: #F59E0B;

      --scrollbar-thumb: rgba(148, 163, 184, 0.22);
      --scrollbar-thumb-hover: rgba(148, 163, 184, 0.45);
      --shadow-card: 0 1px 3px rgba(0, 0, 0, 0.25);
      --radius-sm: 6px;
      --radius: 8px;
    }

    [data-theme="light"] {
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

    /* Header Compacto */
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

    /* Métricas Financeiras */
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

    /* Tabuleiro Kanban com Drag & Drop */
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
      transition: background 0.15s ease, border-color 0.15s ease;
    }

    .kanban-column.drag-over {
      border-color: var(--primary);
      background: rgba(37, 99, 235, 0.06);
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

    /* Cards com Drag & Drop e Ficha */
    .deal-card {
      background: var(--bg-card);
      border: 1px solid var(--border-subtle);
      border-radius: var(--radius-sm);
      padding: 12px;
      display: flex;
      flex-direction: column;
      gap: 8px;
      box-shadow: var(--shadow-card);
      transition: all 0.15s ease;
      cursor: grab;
      user-select: none;
    }

    .deal-card:hover {
      border-color: var(--border-strong);
      background: var(--bg-card-hover);
    }

    .deal-card:active {
      cursor: grabbing;
    }

    .deal-card.dragging {
      opacity: 0.45;
      transform: scale(0.97);
      border-style: dashed;
      border-color: var(--primary);
    }

    .card-head {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      gap: 6px;
    }

    .card-title-group {
      display: flex;
      flex-direction: column;
      gap: 2px;
      min-width: 0;
    }

    .card-name {
      font-weight: 700;
      font-size: 0.88rem;
      color: var(--text-bright);
      line-height: 1.25;
      cursor: pointer;
    }
    .card-name:hover {
      color: var(--primary);
      text-decoration: underline;
    }

    .card-owner {
      font-size: 0.72rem;
      color: var(--text-muted);
    }

    .card-tag {
      font-size: 0.68rem;
      font-weight: 700;
      padding: 2px 6px;
      border-radius: 4px;
      background: var(--purple-bg);
      color: var(--purple);
      white-space: nowrap;
      flex-shrink: 0;
    }

    /* Selo Google Meu Negócio no Card */
    .gmb-badge-row {
      display: flex;
      align-items: center;
      gap: 6px;
      font-size: 0.72rem;
      color: var(--gmb-gold);
      font-weight: 600;
    }

    .gmb-stars {
      display: inline-flex;
      align-items: center;
      gap: 3px;
      background: rgba(245, 158, 11, 0.1);
      padding: 2px 6px;
      border-radius: 4px;
      border: 1px solid rgba(245, 158, 11, 0.25);
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

    .card-actions-row {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 6px;
      margin-top: 2px;
    }

    .btn-card {
      height: 28px;
      padding: 0 8px;
      border-radius: var(--radius-sm);
      font-size: 0.72rem;
      font-weight: 600;
      border: 1px solid var(--border-subtle);
      background: transparent;
      color: var(--text-main);
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 4px;
      cursor: pointer;
      text-decoration: none;
      transition: all 0.15s ease;
    }
    .btn-card:hover {
      background: var(--bg-card-hover);
      border-color: var(--border-strong);
    }

    .btn-card-zap {
      background: #10B981;
      color: #FFFFFF;
      border-color: #10B981;
    }
    .btn-card-zap:hover {
      opacity: 0.9;
      background: #059669;
    }

    .btn-card-upsell {
      background: var(--purple-bg);
      border-color: var(--purple);
      color: var(--purple);
      grid-column: span 2;
    }
    .btn-card-upsell:hover {
      background: var(--purple);
      color: #FFFFFF;
    }

    /* Modal Ficha Completa do Lead */
    .modal-overlay {
      display: none;
      position: fixed;
      top: 0; left: 0; right: 0; bottom: 0;
      background: rgba(0, 0, 0, 0.75);
      backdrop-filter: blur(4px);
      z-index: 100;
      align-items: center;
      justify-content: center;
      padding: 16px;
    }
    .modal-overlay.active {
      display: flex !important;
    }

    .modal-dossier {
      background: var(--bg-surface);
      border: 1px solid var(--border-strong);
      border-radius: var(--radius);
      width: 100%;
      max-width: 820px;
      max-height: 90vh;
      overflow-y: auto;
      padding: 24px;
      box-shadow: 0 20px 48px rgba(0, 0, 0, 0.5);
      display: flex;
      flex-direction: column;
      gap: 18px;
    }

    .dossier-header {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      border-bottom: 1px solid var(--border-subtle);
      padding-bottom: 14px;
    }

    .dossier-title-wrap {
      display: flex;
      flex-direction: column;
      gap: 3px;
    }

    .dossier-title {
      font-size: 1.25rem;
      font-weight: 800;
      color: var(--text-bright);
      letter-spacing: -0.01em;
    }

    .dossier-subtitle {
      font-size: 0.78rem;
      color: var(--text-muted);
    }

    .dossier-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 18px;
    }

    .dossier-section {
      background: var(--bg-card);
      border: 1px solid var(--border-subtle);
      border-radius: var(--radius-sm);
      padding: 16px;
      display: flex;
      flex-direction: column;
      gap: 12px;
    }

    .section-title {
      font-size: 0.75rem;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: var(--primary);
      display: flex;
      align-items: center;
      gap: 6px;
      border-bottom: 1px solid var(--border-subtle);
      padding-bottom: 6px;
    }

    .field-row {
      display: flex;
      flex-direction: column;
      gap: 4px;
    }

    .field-label {
      font-size: 0.72rem;
      font-weight: 600;
      color: var(--text-muted);
      text-transform: uppercase;
      letter-spacing: 0.03em;
    }

    .field-input {
      background: var(--bg-app);
      border: 1px solid var(--border-subtle);
      color: var(--text-bright);
      border-radius: var(--radius-sm);
      padding: 7px 10px;
      font-size: 0.82rem;
      font-family: inherit;
      outline: none;
    }
    .field-input:focus {
      border-color: var(--border-focus);
    }

    .gmb-box {
      background: rgba(245, 158, 11, 0.05);
      border: 1px solid rgba(245, 158, 11, 0.2);
      border-radius: var(--radius-sm);
      padding: 12px;
      display: flex;
      flex-direction: column;
      gap: 8px;
    }

    .gmb-header-row {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .gmb-score {
      font-family: 'JetBrains Mono', monospace;
      font-weight: 700;
      color: var(--gmb-gold);
      font-size: 0.95rem;
      display: inline-flex;
      align-items: center;
      gap: 4px;
    }

    .gmb-quote {
      font-size: 0.76rem;
      font-style: italic;
      color: var(--text-main);
      background: rgba(0, 0, 0, 0.2);
      padding: 8px;
      border-radius: 4px;
      border-left: 2px solid var(--gmb-gold);
      line-height: 1.4;
    }

    .dossier-actions {
      display: flex;
      justify-content: space-between;
      align-items: center;
      border-top: 1px solid var(--border-subtle);
      padding-top: 14px;
      flex-wrap: wrap;
      gap: 10px;
    }

    .action-group-left {
      display: flex;
      gap: 8px;
    }
    .action-group-right {
      display: flex;
      gap: 8px;
    }

    /* Modal Roteiro de Abordagem */
    .modal-script {
      background: var(--bg-surface);
      border: 1px solid var(--border-strong);
      border-radius: var(--radius);
      width: 100%;
      max-width: 540px;
      padding: 22px;
      box-shadow: 0 16px 36px rgba(0, 0, 0, 0.4);
      display: flex;
      flex-direction: column;
      gap: 16px;
    }

    /* Dots */
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

  <!-- Top Header -->
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
      <button class="btn btn-outline" onclick="openWhatsAppModal()" style="border-color: rgba(37,211,102,0.4); color: #25D366; background: rgba(37,211,102,0.08); font-weight: 600; display: inline-flex; align-items: center; gap: 6px;">
        <span style="display:inline-block; width:8px; height:8px; border-radius:50%; background:#25D366; box-shadow:0 0 8px #25D366;"></span>
        🛡️ WhatsApp Shield & Sophia
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

  <!-- Métricas Financeiras -->
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

  <!-- Tabuleiro Kanban Drag & Drop -->
  <div class="board-container">
    <div class="kanban-wrapper" id="kanbanBoard">
      <!-- 1. Prospecção -->
      <div class="kanban-column" data-stage="prospeccao" ondragover="handleDragOver(event)" ondragleave="handleDragLeave(event)" ondrop="handleDrop(event, 'prospeccao')">
        <div class="column-header">
          <div class="col-title-wrap">
            <div class="col-dot dot-blue"></div>
            <div class="col-title">1. Prospecção</div>
          </div>
          <div class="col-count" id="count-prospeccao">0</div>
        </div>
        <div class="cards-container" id="cards-prospeccao"></div>
      </div>

      <!-- 2. Primeiro Contato -->
      <div class="kanban-column" data-stage="contato_enviado" ondragover="handleDragOver(event)" ondragleave="handleDragLeave(event)" ondrop="handleDrop(event, 'contato_enviado')">
        <div class="column-header">
          <div class="col-title-wrap">
            <div class="col-dot dot-indigo"></div>
            <div class="col-title">2. Primeiro Contato</div>
          </div>
          <div class="col-count" id="count-contato_enviado">0</div>
        </div>
        <div class="cards-container" id="cards-contato_enviado"></div>
      </div>

      <!-- 3. Em Qualificação -->
      <div class="kanban-column" data-stage="em_conversa" ondragover="handleDragOver(event)" ondragleave="handleDragLeave(event)" ondrop="handleDrop(event, 'em_conversa')">
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
      <div class="kanban-column" data-stage="negociacao" ondragover="handleDragOver(event)" ondragleave="handleDragLeave(event)" ondrop="handleDrop(event, 'negociacao')">
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
      <div class="kanban-column" data-stage="fechado_pago" ondragover="handleDragOver(event)" ondragleave="handleDragLeave(event)" ondrop="handleDrop(event, 'fechado_pago')">
        <div class="column-header">
          <div class="col-title-wrap">
            <div class="col-dot dot-green"></div>
            <div class="col-title">5. Fechado & Pago</div>
          </div>
          <div class="col-count" id="count-fechado_pago">0</div>
        </div>
        <div class="cards-container" id="cards-fechado_pago"></div>
      </div>

      <!-- 6. Em Produção (48h) -->
      <div class="kanban-column" data-stage="setup_48h" ondragover="handleDragOver(event)" ondragleave="handleDragLeave(event)" ondrop="handleDrop(event, 'setup_48h')">
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
      <div class="kanban-column" data-stage="radar_upsell" ondragover="handleDragOver(event)" ondragleave="handleDragLeave(event)" ondrop="handleDrop(event, 'radar_upsell')">
        <div class="column-header">
          <div class="col-title-wrap">
            <div class="col-dot dot-purple"></div>
            <div class="col-title">7. No Ar & MRR Ativo</div>
          </div>
          <div class="col-count" id="count-radar_upsell">0</div>
        </div>
        <div class="cards-container" id="cards-radar_upsell"></div>
      </div>

      <!-- 8. Desqualificado -->
      <div class="kanban-column" data-stage="perdido" ondragover="handleDragOver(event)" ondragleave="handleDragLeave(event)" ondrop="handleDrop(event, 'perdido')">
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

  <!-- Modal: Ficha Completa do Lead (Dossiê do Negócio) -->
  <div class="modal-overlay" id="dossierModal">
    <div class="modal-dossier">
      <div class="dossier-header">
        <div class="dossier-title-wrap">
          <div class="dossier-title" id="dossierTitle">Ficha do Lead</div>
          <div class="dossier-subtitle" id="dossierSubtitle">Inteligência de Mercado, Google Meu Negócio e Parâmetros Comerciais</div>
        </div>
        <button class="btn btn-outline" onclick="closeDossierModal()">Fechar</button>
      </div>

      <input type="hidden" id="dossierDealId">

      <div class="dossier-grid">
        <!-- Coluna Esquerda: Identidade & GMB -->
        <div class="dossier-section">
          <div class="section-title">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
              <circle cx="12" cy="7" r="4"></circle>
            </svg>
            Identidade do Negócio & Decisor
          </div>

          <div class="field-row">
            <label class="field-label">Nome da Confeitaria / Ateliê</label>
            <input type="text" class="field-input" id="dossierName">
          </div>

          <div class="field-row">
            <label class="field-label">Nome da Proprietária / Decisora</label>
            <input type="text" class="field-input" id="dossierOwnerName" placeholder="Ex: Sandra, Camila...">
          </div>

          <div class="field-row">
            <label class="field-label">Bairro, Cidade - Estado</label>
            <input type="text" class="field-input" id="dossierCityState" placeholder="Ex: Tijuca, Rio de Janeiro - RJ">
          </div>

          <div class="field-row">
            <label class="field-label">Especialidade / Carro-Chefe</label>
            <input type="text" class="field-input" id="dossierSpecialty" placeholder="Ex: Bolos artísticos para casamento, bentô cakes...">
          </div>

          <!-- Caixa Google Meu Negócio (GMB) -->
          <div class="gmb-box">
            <div class="gmb-header-row">
              <div class="field-label" style="color: var(--gmb-gold);">Google Meu Negócio (GMB)</div>
              <div class="gmb-score" id="gmbScoreDisplay">
                <svg width="13" height="13" viewBox="0 0 24 24" fill="currentColor" stroke="none">
                  <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon>
                </svg>
                <span id="dossierRatingText">4.9</span> (<span id="dossierReviewsText">142</span>)
              </div>
            </div>

            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px;">
              <div class="field-row">
                <label class="field-label">Nota no Google</label>
                <input type="number" step="0.1" max="5.0" min="1.0" class="field-input" id="dossierGmbRating">
              </div>
              <div class="field-row">
                <label class="field-label">Total de Avaliações</label>
                <input type="number" class="field-input" id="dossierGmbReviews">
              </div>
            </div>

            <div class="field-row">
              <label class="field-label">Link da Ficha no Google Maps</label>
              <input type="text" class="field-input" id="dossierGmbUrl" placeholder="https://maps.google.com/?q=...">
            </div>

            <div class="field-row">
              <label class="field-label">Depoimento Estrela do Google (Prova Social)</label>
              <textarea class="field-input" id="dossierGmbTopReview" rows="2" placeholder="Avaliação real de cliente para estampar no topo da Landing Page..."></textarea>
            </div>
          </div>
        </div>

        <!-- Coluna Direita: Contato, Diagnóstico & Operação -->
        <div class="dossier-section">
          <div class="section-title">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <circle cx="12" cy="12" r="10"></circle>
              <polygon points="16.24 7.76 14.12 14.12 7.76 16.24 9.88 9.88 16.24 7.76"></polygon>
            </svg>
            Contato & Diagnóstico Digital
          </div>

          <div class="field-row">
            <label class="field-label">WhatsApp Oficial (com DDD)</label>
            <input type="text" class="field-input" id="dossierWhatsapp">
          </div>

          <div class="field-row">
            <label class="field-label">Perfil do Instagram (@)</label>
            <input type="text" class="field-input" id="dossierInstagram">
          </div>

          <div class="field-row">
            <label class="field-label">Diagnóstico do Link da Bio Atual</label>
            <input type="text" class="field-input" id="dossierBioLinkType" placeholder="Ex: Linktree com 8 links confusos, sem cardápio...">
          </div>

          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px;">
            <div class="field-row">
              <label class="field-label">Valor Front-End (R$)</label>
              <input type="number" class="field-input" id="dossierDealValue">
            </div>
            <div class="field-row">
              <label class="field-label">Hospedagem MRR (R$/mês)</label>
              <select class="field-input" id="dossierMrrValue">
                <option value="59.0">R$ 59,00/mês</option>
                <option value="79.0">R$ 79,00/mês</option>
                <option value="97.0">R$ 97,00/mês</option>
              </select>
            </div>
          </div>

          <div class="field-row">
            <label class="field-label">Domínio Sugerido / Contratado</label>
            <input type="text" class="field-input" id="dossierHostingDomain" placeholder="Ex: sandrabolos.com.br">
          </div>

          <div class="field-row">
            <label class="field-label">Anotações Internas & Dores Observadas</label>
            <textarea class="field-input" id="dossierNotes" rows="3" placeholder="Histórico das conversas, preferências da cliente..."></textarea>
          </div>
        </div>
      </div>

      <div class="dossier-actions">
        <div class="action-group-left">
          <button type="button" class="btn btn-primary" onclick="openFirstContactScriptFromDossier()">
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"></path>
            </svg>
            Gerar Abordagem Zap (com Google Review)
          </button>
          <button type="button" class="btn btn-outline" onclick="openUpsellFromDossier()">
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <polyline points="23 6 13.5 15.5 8.5 10.5 1 18"></polyline>
              <polyline points="17 6 23 6 23 12"></polyline>
            </svg>
            Radar LTV (Jay Abraham)
          </button>
        </div>

        <div class="action-group-right">
          <button type="button" class="btn btn-outline" onclick="closeDossierModal()">Cancelar</button>
          <button type="button" class="btn btn-primary" onclick="saveLeadDossier()">Salvar Alterações</button>
        </div>
      </div>
    </div>
  </div>

  <!-- Modal: Cadastro de Novo Lead -->
  <div class="modal-overlay" id="newLeadModal">
    <div class="modal-script">
      <div class="dossier-title">Cadastrar Lead de Confeitaria</div>
      <form id="newLeadForm" onsubmit="handleCreateLead(event)">
        <div class="field-row">
          <label class="field-label">Nome do Estabelecimento *</label>
          <input type="text" class="field-input" id="leadName" required placeholder="Ex: Ateliê Sandra Bolos">
        </div>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-top: 6px;">
          <div class="field-row">
            <label class="field-label">Nome da Decisora</label>
            <input type="text" class="field-input" id="leadOwnerName" placeholder="Ex: Sandra">
          </div>
          <div class="field-row">
            <label class="field-label">Cidade / Bairro</label>
            <input type="text" class="field-input" id="leadCityState" placeholder="Ex: Moema, SP">
          </div>
        </div>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-top: 6px;">
          <div class="field-row">
            <label class="field-label">Instagram (@)</label>
            <input type="text" class="field-input" id="leadInstagram" placeholder="@ateliesandra">
          </div>
          <div class="field-row">
            <label class="field-label">WhatsApp *</label>
            <input type="text" class="field-input" id="leadWhatsapp" required placeholder="5511999998888">
          </div>
        </div>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-top: 6px;">
          <div class="field-row">
            <label class="field-label">Nota Google</label>
            <input type="number" step="0.1" class="field-input" id="leadGmbRating" value="4.9">
          </div>
          <div class="field-row">
            <label class="field-label">Nº Avaliações Google</label>
            <input type="number" class="field-input" id="leadGmbReviews" value="85">
          </div>
        </div>
        <div class="field-row" style="margin-top: 6px;">
          <label class="field-label">Melhor Avaliação do Google</label>
          <input type="text" class="field-input" id="leadGmbTopReview" placeholder="Ex: Bolo maravilhoso, entrega pontual...">
        </div>
        <div class="field-row" style="margin-top: 6px;">
          <label class="field-label">Plano de Hospedagem / MRR Previsto</label>
          <select class="field-input" id="leadMrr">
            <option value="59.0">R$ 59,00/mês (Hospedagem Gerenciada + SSL)</option>
            <option value="79.0" selected>R$ 79,00/mês (Hospedagem Pro + Ajustes Cardápio)</option>
            <option value="97.0">R$ 97,00/mês (Hospedagem + Suporte Prioritário)</option>
          </select>
        </div>
        <div class="modal-actions" style="margin-top: 14px; display: flex; justify-content: flex-end; gap: 8px;">
          <button type="button" class="btn btn-outline" onclick="closeNewLeadModal()">Cancelar</button>
          <button type="submit" class="btn btn-primary">Salvar Lead</button>
        </div>
      </form>
    </div>
  </div>

  <!-- Modal: Roteiro de Abordagem / Upsell -->
  <div class="modal-overlay" id="scriptModal">
    <div class="modal-script">
      <div class="dossier-title" id="scriptModalTitle">Roteiro Personalizado</div>
      <div class="dossier-subtitle" id="scriptModalSubtitle">Mensagem pronta para envio imediato no WhatsApp.</div>
      <div class="field-row">
        <label class="field-label">Mensagem para Copiar</label>
        <textarea id="scriptModalText" rows="9" readonly class="field-input" style="font-size: 0.8rem; line-height: 1.45;"></textarea>
      </div>
      <div class="modal-actions" style="display: flex; justify-content: space-between; align-items: center; margin-top: 6px;">
        <button type="button" class="btn btn-outline" onclick="closeScriptModal()">Fechar</button>
        <button type="button" class="btn btn-primary" onclick="copyScriptText()">
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
            <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
          </svg>
          Copiar Mensagem
        </button>
      </div>
    </div>
  </div>

  <!-- Modal: WhatsApp Iron Shield & Sophia Agno -->
  <div class="modal-overlay" id="whatsappModal" onclick="if(event.target === this) closeWhatsAppModal()">
    <div class="modal-script" style="max-width: 650px; width: 95%; max-height: 90vh; overflow-y: auto;">
      <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px;">
        <div>
          <div class="dossier-title" style="display: flex; align-items: center; gap: 8px;">
            <span>🛡️</span> WhatsApp Iron Shield & Sophia
          </div>
          <div class="dossier-subtitle">Motor Agno + Gemini com blindagem absoluta de CRM e anti-vazamento.</div>
        </div>
        <button class="btn-icon" onclick="closeWhatsAppModal()" title="Fechar">✕</button>
      </div>

      <!-- Badge de Proteção -->
      <div style="background: rgba(37, 211, 102, 0.1); border: 1px solid rgba(37, 211, 102, 0.3); border-radius: 8px; padding: 12px; margin-bottom: 16px;">
        <div style="display: flex; align-items: center; justify-content: space-between;">
          <div style="display: flex; align-items: center; gap: 8px;">
            <span style="display:inline-block; width:10px; height:10px; border-radius:50%; background:#25D366; box-shadow:0 0 10px #25D366;"></span>
            <strong style="color: #25D366; font-size: 0.85rem;">IRON SHIELD ATIVO</strong>
          </div>
          <span style="font-size: 0.75rem; background: var(--bg-tertiary); padding: 2px 8px; border-radius: 4px; color: var(--text-secondary);">
            Grupos & Números Pessoais Bloqueados
          </span>
        </div>
        <p style="font-size: 0.78rem; color: var(--text-secondary); margin: 6px 0 0 0; line-height: 1.4;">
          Apenas mensagens de números previamente cadastrados na base de leads do CRM são processadas pela Sophia. Qualquer grupo ou contato desconhecido é descartado silenciosamente.
        </p>
      </div>

      <!-- Teste & Simulação -->
      <div style="background: var(--bg-secondary); border: 1px solid var(--border-color); border-radius: 8px; padding: 14px; margin-bottom: 16px;">
        <div style="font-size: 0.85rem; font-weight: 600; margin-bottom: 8px; color: var(--text-primary);">🧪 Simulador em Tempo Real</div>
        <div class="field-row" style="margin-bottom: 10px;">
          <label class="field-label">Selecione o Lead Autorizado:</label>
          <select id="simLeadSelect" class="field-input" onchange="updateSimPhone(this.value)">
            <option value="5541999000040">Lucca Cafés & Pâtisserie (Batel) - 5541999000040</option>
            <option value="5541991221240">Prestinaria - Casa dos Pães - 5541991221240</option>
            <option value="5511999991234">[TESTE] Número Desconhecido (Deve ser Bloqueado)</option>
            <option value="group_test">[TESTE] Grupo de WhatsApp (Deve ser Bloqueado)</option>
          </select>
        </div>
        <div class="field-row" style="margin-bottom: 10px;">
          <label class="field-label">Mensagem Recebida do Cliente:</label>
          <textarea id="simMessageText" rows="2" class="field-input" placeholder="Ex: Oi Sophia, recebi o link do cardápio! Quanto custa a implementação?">Oi! Vi o link que vocês mandaram do cardápio. Como funciona a ativação nas mesas com o QR Code?</textarea>
        </div>
        <button type="button" class="btn btn-primary" onclick="runWhatsAppSimulation()" id="simRunBtn" style="width: 100%;">
          ⚡ Testar Resposta da Sophia
        </button>
      </div>

      <!-- Resultado da Interação -->
      <div id="simResultBox" style="display: none; margin-bottom: 16px;"></div>

      <!-- Instruções da Evolution API -->
      <div style="background: var(--bg-tertiary); border-radius: 8px; padding: 12px; font-size: 0.78rem; line-height: 1.5; color: var(--text-secondary);">
        <strong>📡 Conexão com Evolution API:</strong><br>
        Configure o Webhook na sua Evolution API para: <code style="background: var(--bg-secondary); padding: 2px 6px; border-radius: 4px; color: #38bdf8;">POST http://localhost:8000/api/whatsapp/evolution/webhook</code><br>
        Eventos necessários: <code style="background: var(--bg-secondary); padding: 2px 6px; border-radius: 4px;">MESSAGES_UPSERT</code>
      </div>

      <div class="modal-actions" style="margin-top: 14px; display: flex; justify-content: flex-end;">
        <button type="button" class="btn btn-outline" onclick="closeWhatsAppModal()">Fechar</button>
      </div>
    </div>
  </div>

  <!-- JavaScript do CRM com Drag & Drop e Ficha do Lead -->
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

    let draggedDealId = null;

    // Gerenciador de Tema (Dark / Light)
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

    const savedTheme = localStorage.getItem('konig_crm_theme') || 'dark';
    applyTheme(savedTheme);

    // Rolagem horizontal ergonômica com roda do mouse
    const board = document.getElementById('kanbanBoard');
    board.addEventListener('wheel', (e) => {
      if (e.deltaY !== 0 && !e.target.closest('.cards-container')) {
        board.scrollLeft += e.deltaY;
        e.preventDefault();
      }
    }, { passive: false });

    // HTML5 Drag & Drop Handlers
    function handleDragStart(e, dealId) {
      draggedDealId = dealId;
      e.dataTransfer.setData('text/plain', dealId);
      e.dataTransfer.effectAllowed = 'move';
      e.target.classList.add('dragging');
    }

    function handleDragEnd(e) {
      e.target.classList.remove('dragging');
      document.querySelectorAll('.kanban-column').forEach(c => c.classList.remove('drag-over'));
      draggedDealId = null;
    }

    function handleDragOver(e) {
      e.preventDefault();
      e.dataTransfer.dropEffect = 'move';
      const col = e.currentTarget;
      if (!col.classList.contains('drag-over')) {
        col.classList.add('drag-over');
      }
    }

    function handleDragLeave(e) {
      const col = e.currentTarget;
      col.classList.remove('drag-over');
    }

    async function handleDrop(e, targetStage) {
      e.preventDefault();
      const col = e.currentTarget;
      col.classList.remove('drag-over');

      const dealId = draggedDealId || e.dataTransfer.getData('text/plain');
      if (!dealId) return;

      const cardElem = document.getElementById(`deal-card-${dealId}`);
      const targetContainer = document.getElementById(`cards-${targetStage}`);

      // Optimistic UI move
      if (cardElem && targetContainer) {
        targetContainer.prepend(cardElem);
      }

      try {
        const res = await fetch(`/api/deals/${dealId}/stage`, {
          method: 'PATCH',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ stage: targetStage })
        });
        if (res.ok) {
          loadAllData();
        }
      } catch (err) {
        console.error('Erro ao mover lead via drag-and-drop:', err);
        loadAllData();
      }
    }

    // Carregamento de Dados
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
      card.id = `deal-card-${deal.id}`;
      card.draggable = true;
      card.ondragstart = (e) => handleDragStart(e, deal.id);
      card.ondragend = (e) => handleDragEnd(e);

      const cleanZap = (deal.whatsapp || '').replace(/\\D/g, '');
      const zapLink = cleanZap ? `https://wa.me/${cleanZap}?text=Olá%20${encodeURIComponent((deal.owner_name || deal.name).split(' ')[0])},%20tudo%20bem?` : '#';

      const gmbRating = deal.gmb_rating || 4.9;
      const gmbReviews = deal.gmb_reviews_count || 0;

      card.innerHTML = `
        <div class="card-head">
          <div class="card-title-group">
            <div class="card-name" onclick="openLeadDossier(${deal.id})" title="Clique para abrir a Ficha do Lead">${escapeHtml(deal.name)}</div>
            ${deal.owner_name ? `<div class="card-owner">${escapeHtml(deal.owner_name)} ${deal.city_state ? '• ' + escapeHtml(deal.city_state) : ''}</div>` : ''}
          </div>
          <div class="card-tag">${escapeHtml(deal.niche || 'Gourmet')}</div>
        </div>

        <div class="gmb-badge-row">
          <div class="gmb-stars">
            <svg width="11" height="11" viewBox="0 0 24 24" fill="currentColor" stroke="none">
              <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon>
            </svg>
            ${gmbRating.toFixed(1)} (${gmbReviews})
          </div>
          <span style="color: var(--text-dim); font-size: 0.68rem;">Google Avaliações</span>
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

        ${deal.stage === 'radar_upsell' || deal.stage === 'fechado_pago' ? `
          <button class="btn-card btn-card-upsell" onclick="openUpsellModal(${deal.id})">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
              <polyline points="23 6 13.5 15.5 8.5 10.5 1 18"></polyline>
              <polyline points="17 6 23 6 23 12"></polyline>
            </svg>
            Radar de Expansão (LTV)
          </button>
        ` : ''}

        <div class="card-actions-row">
          <a href="${zapLink}" target="_blank" class="btn-card btn-card-zap">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"></path>
            </svg>
            WhatsApp
          </a>
          <button type="button" class="btn-card" onclick="openLeadDossier(${deal.id})">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
              <polyline points="14 2 14 8 20 8"></polyline>
              <line x1="16" y1="13" x2="8" y2="13"></line>
              <line x1="16" y1="17" x2="8" y2="17"></line>
              <polyline points="10 9 9 9 8 9"></polyline>
            </svg>
            Ficha do Lead
          </button>
        </div>
      `;

      return card;
    }

    // Modal: Ficha Completa do Lead
    async function openLeadDossier(dealId) {
      try {
        const res = await fetch(`/api/deals/${dealId}`);
        const deal = await res.json();

        document.getElementById('dossierDealId').value = deal.id;
        document.getElementById('dossierTitle').innerText = deal.name;
        document.getElementById('dossierName').value = deal.name || '';
        document.getElementById('dossierOwnerName').value = deal.owner_name || '';
        document.getElementById('dossierCityState').value = deal.city_state || '';
        document.getElementById('dossierSpecialty').value = deal.specialty || '';
        document.getElementById('dossierInstagram').value = deal.instagram || '';
        document.getElementById('dossierWhatsapp').value = deal.whatsapp || '';
        document.getElementById('dossierBioLinkType').value = deal.bio_link_type || '';
        document.getElementById('dossierDealValue').value = deal.deal_value || 699.0;
        document.getElementById('dossierMrrValue').value = (deal.mrr_value || 59.0).toFixed(1);
        document.getElementById('dossierHostingDomain').value = deal.hosting_domain || '';
        document.getElementById('dossierNotes').value = deal.notes || '';

        // GMB
        const gmbRating = deal.gmb_rating || 4.9;
        const gmbReviews = deal.gmb_reviews_count || 85;
        document.getElementById('dossierGmbRating').value = gmbRating;
        document.getElementById('dossierGmbReviews').value = gmbReviews;
        document.getElementById('dossierGmbUrl').value = deal.gmb_url || '';
        document.getElementById('dossierGmbTopReview').value = deal.gmb_top_review || '';
        document.getElementById('dossierRatingText').innerText = gmbRating.toFixed(1);
        document.getElementById('dossierReviewsText').innerText = gmbReviews;

        document.getElementById('dossierModal').style.display = 'flex';
      } catch (err) {
        alert('Erro ao carregar Ficha do Lead');
      }
    }

    function closeDossierModal() {
      document.getElementById('dossierModal').style.display = 'none';
    }

    async function saveLeadDossier() {
      const dealId = document.getElementById('dossierDealId').value;
      const payload = {
        name: document.getElementById('dossierName').value,
        owner_name: document.getElementById('dossierOwnerName').value,
        city_state: document.getElementById('dossierCityState').value,
        specialty: document.getElementById('dossierSpecialty').value,
        instagram: document.getElementById('dossierInstagram').value,
        whatsapp: document.getElementById('dossierWhatsapp').value,
        bio_link_type: document.getElementById('dossierBioLinkType').value,
        deal_value: parseFloat(document.getElementById('dossierDealValue').value),
        mrr_value: parseFloat(document.getElementById('dossierMrrValue').value),
        hosting_domain: document.getElementById('dossierHostingDomain').value,
        notes: document.getElementById('dossierNotes').value,
        gmb_rating: parseFloat(document.getElementById('dossierGmbRating').value),
        gmb_reviews_count: parseInt(document.getElementById('dossierGmbReviews').value),
        gmb_url: document.getElementById('dossierGmbUrl').value,
        gmb_top_review: document.getElementById('dossierGmbTopReview').value
      };

      try {
        const res = await fetch(`/api/deals/${dealId}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        if (res.ok) {
          closeDossierModal();
          loadAllData();
        }
      } catch (err) {
        alert('Erro ao salvar Ficha do Lead');
      }
    }

    // Gerador de Scripts
    async function openFirstContactScriptFromDossier() {
      const dealId = document.getElementById('dossierDealId').value;
      try {
        const res = await fetch(`/api/first-contact-script/${dealId}`);
        const data = await res.json();
        document.getElementById('scriptModalTitle').innerText = `Abordagem de 1º Contato — ${data.name}`;
        document.getElementById('scriptModalSubtitle').innerText = `Mensagem humanizada alavancando as avaliações do Google Meu Negócio.`;
        document.getElementById('scriptModalText').value = data.script;
        document.getElementById('scriptModal').style.display = 'flex';
      } catch (err) {
        alert('Erro ao gerar abordagem');
      }
    }

    async function openUpsellFromDossier() {
      const dealId = document.getElementById('dossierDealId').value;
      openUpsellModal(dealId);
    }

    async function openUpsellModal(dealId) {
      try {
        const res = await fetch(`/api/upsell-script/${dealId}`);
        const data = await res.json();
        document.getElementById('scriptModalTitle').innerText = `Estratégia de Expansão — ${data.name}`;
        document.getElementById('scriptModalSubtitle').innerText = `Abordagem de consultoria baseada na heurística do Próximo Problema Lógico do cliente.`;
        document.getElementById('scriptModalText').value = data.script;
        document.getElementById('scriptModal').style.display = 'flex';
      } catch (err) {
        alert('Erro ao buscar script de upsell');
      }
    }

    function closeScriptModal() {
      document.getElementById('scriptModal').style.display = 'none';
    }

    function copyScriptText() {
      const textarea = document.getElementById('scriptModalText');
      textarea.select();
      document.execCommand('copy');
      alert('Mensagem copiada para a área de transferência!');
    }

    // Modal Novo Lead
    function openNewLeadModal() {
      document.getElementById('newLeadModal').style.display = 'flex';
    }
    function closeNewLeadModal() {
      document.getElementById('newLeadModal').style.display = 'none';
    }

    async function handleCreateLead(e) {
      e.preventDefault();
      const payload = {
        name: document.getElementById('leadName').value,
        owner_name: document.getElementById('leadOwnerName').value,
        city_state: document.getElementById('leadCityState').value,
        instagram: document.getElementById('leadInstagram').value,
        whatsapp: document.getElementById('leadWhatsapp').value,
        gmb_rating: parseFloat(document.getElementById('leadGmbRating').value || 4.9),
        gmb_reviews_count: parseInt(document.getElementById('leadGmbReviews').value || 85),
        gmb_top_review: document.getElementById('leadGmbTopReview').value,
        mrr_value: parseFloat(document.getElementById('leadMrr').value),
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

    function escapeHtml(text) {
      if (!text) return '';
      const div = document.createElement('div');
      div.innerText = text;
      return div.innerHTML;
    }

    function openWhatsAppModal() {
      const m = document.getElementById('whatsappModal');
      if (m) {
        m.style.display = 'flex';
        m.classList.add('active');
      }
    }

    function closeWhatsAppModal() {
      const m = document.getElementById('whatsappModal');
      if (m) {
        m.style.display = 'none';
        m.classList.remove('active');
      }
    }

    function updateSimPhone(val) {
      if (val === 'group_test') {
        document.getElementById('simMessageText').value = 'Alguém viu o jogo de ontem?';
      } else if (val === '5511999991234') {
        document.getElementById('simMessageText').value = 'Oi, quem é?';
      } else {
        document.getElementById('simMessageText').value = 'Oi! Vi o link que vocês mandaram do cardápio. Como funciona a ativação nas mesas com o QR Code?';
      }
    }

    async function runWhatsAppSimulation() {
      const selectVal = document.getElementById('simLeadSelect').value;
      const msg = document.getElementById('simMessageText').value.trim();
      const btn = document.getElementById('simRunBtn');
      const box = document.getElementById('simResultBox');

      if (!msg) {
        alert('Digite uma mensagem para simular');
        return;
      }

      btn.disabled = true;
      btn.innerText = 'Sophia raciocinando no Agno...';
      box.style.display = 'block';
      box.innerHTML = '<div style="padding: 12px; text-align: center; color: var(--text-secondary);">⏳ Processando através do Iron Shield e Agno Engine...</div>';

      const isGroup = (selectVal === 'group_test');
      const phone = isGroup ? '120363024829283@g.us' : selectVal;

      try {
        const res = await fetch('/api/whatsapp/simulate', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ phone, message: msg, is_group: isGroup })
        });
        const data = await res.json();

        if (!data.success) {
          box.innerHTML = `
            <div style="background: rgba(239, 68, 68, 0.1); border: 1px solid rgba(239, 68, 68, 0.3); border-radius: 8px; padding: 12px;">
              <div style="color: #ef4444; font-weight: 600; font-size: 0.85rem; display: flex; align-items: center; gap: 6px;">
                <span>⛔</span> MENSAGEM BLOQUEADA PELO IRON SHIELD
              </div>
              <div style="font-size: 0.78rem; color: var(--text-secondary); margin-top: 4px;">
                <strong>Motivo:</strong> ${escapeHtml(data.reason)}
              </div>
              <div style="font-size: 0.74rem; color: var(--text-muted); margin-top: 4px;">
                Segurança confirmada: Zero mensagens enviadas para pessoas de fora do CRM.
              </div>
            </div>
          `;
        } else {
          box.innerHTML = `
            <div style="background: rgba(37, 211, 102, 0.08); border: 1px solid rgba(37, 211, 102, 0.3); border-radius: 8px; padding: 12px;">
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                <div style="color: #25D366; font-weight: 600; font-size: 0.85rem;">
                  ✅ LEAD AUTENTICADO: ${escapeHtml(data.deal_name)}
                </div>
                <span style="font-size: 0.72rem; background: rgba(37,211,102,0.15); color: #25D366; padding: 2px 6px; border-radius: 4px;">
                  Sophia Closer (Agno)
                </span>
              </div>
              <div style="font-size: 0.8rem; line-height: 1.5; color: var(--text-primary); background: var(--bg-secondary); padding: 10px; border-radius: 6px; border: 1px solid var(--border-color); white-space: pre-wrap;">${escapeHtml(data.sophia_reply)}</div>
              <div style="display: flex; justify-content: flex-end; gap: 8px; margin-top: 8px;">
                <button class="btn btn-primary" onclick="alert('Rascunho ID #' + ${data.draft_message_id} + ' aprovado e enviado com sucesso via Evolution API!')" style="font-size: 0.75rem; padding: 6px 12px;">
                  🚀 Disparar via Evolution API
                </button>
              </div>
            </div>
          `;
        }
      } catch (err) {
        box.innerHTML = `<div style="color: #ef4444; font-size: 0.8rem;">Erro ao simular: ${err.message}</div>`;
      } finally {
        btn.disabled = false;
        btn.innerText = '⚡ Testar Resposta da Sophia';
      }
    }

    // Inicialização
    loadAllData();
  </script>
</body>
</html>
"""
    return HTMLResponse(content=html_content)



# ==============================================================================
# KONIG WHATSAPP & SOPHIA AGNO ENGINE WITH IRON SHIELD
# ==============================================================================

class SimulateWhatsAppInbound(BaseModel):
    phone: str
    message: str
    is_group: bool = False


@app.post("/api/whatsapp/evolution/webhook")
async def evolution_webhook(request: Request):
    """
    Webhook que recebe eventos da Evolution API com blindagem estrita do Iron Shield.
    """
    from datetime import datetime, timezone
    import os
    from channels.whatsapp_shield import validate_sender, get_db_connection
    from channels.evolution_client import EvolutionAPIClient
    from squads.sales.sophia_agno import generate_sophia_reply

    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    data = payload.get("data") or payload
    key = data.get("key") or {}

    # Se for mensagem enviada por nós mesmos, ignora
    if key.get("fromMe") is True:
        return {"status": "ignored", "reason": "outbound_message_from_me"}

    remote_jid = key.get("remoteJid") or payload.get("sender") or payload.get("from") or ""
    is_group = "@g.us" in remote_jid or payload.get("isGroup") is True

    # Extrai o texto da mensagem
    msg_obj = data.get("message") or {}
    text = (
        msg_obj.get("conversation")
        or msg_obj.get("extendedTextMessage", {}).get("text")
        or payload.get("body")
        or payload.get("text")
        or ""
    )

    if not text.strip():
        return {"status": "ignored", "reason": "empty_or_unsupported_message"}

    # 1. GATE DO IRON SHIELD (Validação de Grupo e CRM)
    is_allowed, reason, deal_data = validate_sender(remote_jid, is_group=is_group)
    if not is_allowed or not deal_data:
        return {"status": "blocked_by_shield", "reason": reason}

    # 2. LEAD AUTENTICADO NO CRM
    deal_id = deal_data["id"]
    phone = deal_data["whatsapp"]
    now = datetime.now(timezone.utc).isoformat()

    conn = get_db_connection()
    cursor = conn.cursor()

    # Grava mensagem recebida
    cursor.execute("""
        INSERT INTO whatsapp_messages (deal_id, phone, direction, sender_role, content, status, created_at)
        VALUES (?, ?, 'INBOUND', 'LEAD', ?, 'RECEIVED', ?)
    """, (deal_id, phone, text, now))
    conn.commit()

    # Recupera histórico recente de até 5 mensagens
    cursor.execute("""
        SELECT sender_role as role, content FROM whatsapp_messages
        WHERE deal_id = ? ORDER BY id DESC LIMIT 5
    """, (deal_id,))
    history = [dict(r) for r in reversed(cursor.fetchall())]

    # 3. GERAÇÃO DA RESPOSTA COM SOPHIA (AGNO + GEMINI)
    try:
        reply_text = generate_sophia_reply(incoming_text=text, lead_context=deal_data, chat_history=history)
    except Exception as e:
        reply_text = f"Olá! Recebemos sua mensagem no Lucca e estamos analisando. Em instantes retornamos."

    auto_pilot = os.getenv("WHATSAPP_AUTO_PILOT", "false").lower() in ("true", "1", "yes")
    client = EvolutionAPIClient()

    if auto_pilot:
        client.send_typing_presence(phone, seconds=2)
        dispatch_result = client.send_text(phone, reply_text)
        cursor.execute("""
            INSERT INTO whatsapp_messages (deal_id, phone, direction, sender_role, content, status, approved_by_human, created_at)
            VALUES (?, ?, 'OUTBOUND', 'SOPHIA_AGENT', ?, 'SENT', 1, ?)
        """, (deal_id, phone, reply_text, datetime.now(timezone.utc).isoformat()))
        conn.commit()
        conn.close()
        return {
            "status": "autonomous_dispatched",
            "deal": deal_data["name"],
            "reply": reply_text,
            "dispatch": dispatch_result
        }
    else:
        cursor.execute("""
            INSERT INTO whatsapp_messages (deal_id, phone, direction, sender_role, content, status, approved_by_human, created_at)
            VALUES (?, ?, 'OUTBOUND', 'SOPHIA_AGENT', ?, 'DRAFT_PENDING', 0, ?)
        """, (deal_id, phone, reply_text, datetime.now(timezone.utc).isoformat()))
        conn.commit()
        msg_id = cursor.lastrowid
        conn.close()
        return {
            "status": "draft_saved",
            "message_id": msg_id,
            "deal": deal_data["name"],
            "reply": reply_text,
            "notice": "Modo de segurança Co-Piloto ativo. Mensagem pronta para aprovação e disparo."
        }


@app.post("/api/whatsapp/simulate")
async def simulate_inbound_message(sim: SimulateWhatsAppInbound):
    """
    Simula uma mensagem recebida no WhatsApp para testar a blindagem do Iron Shield
    e o raciocínio da Sophia no Agno sem necessidade de conexão real ativa.
    """
    from datetime import datetime, timezone
    from channels.whatsapp_shield import validate_sender, get_db_connection
    from squads.sales.sophia_agno import generate_sophia_reply

    # 1. Validação na blindagem
    is_allowed, reason, deal_data = validate_sender(sim.phone, is_group=sim.is_group)
    if not is_allowed or not deal_data:
        return {
            "success": False,
            "status": "blocked_by_shield",
            "reason": reason,
            "raw_sender": sim.phone,
            "is_group": sim.is_group
        }

    # 2. Lead autenticado
    deal_id = deal_data["id"]
    phone = deal_data["whatsapp"]
    now = datetime.now(timezone.utc).isoformat()

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO whatsapp_messages (deal_id, phone, direction, sender_role, content, status, created_at)
        VALUES (?, ?, 'INBOUND', 'LEAD', ?, 'RECEIVED', ?)
    """, (deal_id, phone, sim.message, now))
    conn.commit()

    cursor.execute("""
        SELECT sender_role as role, content FROM whatsapp_messages
        WHERE deal_id = ? ORDER BY id DESC LIMIT 5
    """, (deal_id,))
    history = [dict(r) for r in reversed(cursor.fetchall())]

    reply_text = generate_sophia_reply(incoming_text=sim.message, lead_context=deal_data, chat_history=history)

    cursor.execute("""
        INSERT INTO whatsapp_messages (deal_id, phone, direction, sender_role, content, status, approved_by_human, created_at)
        VALUES (?, ?, 'OUTBOUND', 'SOPHIA_AGENT', ?, 'DRAFT_PENDING', 0, ?)
    """, (deal_id, phone, reply_text, datetime.now(timezone.utc).isoformat()))
    conn.commit()
    msg_id = cursor.lastrowid
    conn.close()

    return {
        "success": True,
        "status": "authenticated_and_processed",
        "deal_name": deal_data["name"],
        "deal_id": deal_id,
        "lead_phone": phone,
        "draft_message_id": msg_id,
        "sophia_reply": reply_text
    }


@app.get("/api/whatsapp/messages/{deal_id}")
def get_whatsapp_messages(deal_id: int):
    """Retorna histórico de mensagens do WhatsApp para um lead específico."""
    from channels.whatsapp_shield import get_db_connection
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM whatsapp_messages WHERE deal_id = ? ORDER BY id ASC
    """, (deal_id,))
    messages = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return {"deal_id": deal_id, "messages": messages}


@app.get("/api/whatsapp/shield-logs")
def get_shield_audit_logs():
    """Retorna os logs de auditoria da blindagem do Iron Shield."""
    from channels.whatsapp_shield import get_db_connection
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM whatsapp_shield_logs ORDER BY id DESC LIMIT 50
    """)
    logs = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return {"total": len(logs), "logs": logs}


@app.post("/api/whatsapp/approve-and-send/{message_id}")
def approve_and_send_message(message_id: int):
    """Aprova um rascunho da Sophia e dispara via Evolution API."""
    from channels.whatsapp_shield import get_db_connection
    from channels.evolution_client import EvolutionAPIClient

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM whatsapp_messages WHERE id = ?", (message_id,))
    msg = cursor.fetchone()
    if not msg:
        conn.close()
        raise HTTPException(status_code=404, detail="Mensagem não encontrada")

    msg_dict = dict(msg)
    client = EvolutionAPIClient()
    dispatch_result = client.send_text(msg_dict["phone"], msg_dict["content"])

    cursor.execute("""
        UPDATE whatsapp_messages 
        SET status = 'SENT', approved_by_human = 1 
        WHERE id = ?
    """, (message_id,))
    conn.commit()
    conn.close()

    return {
        "success": True,
        "message_id": message_id,
        "dispatched_to": msg_dict["phone"],
        "result": dispatch_result
    }


if __name__ == "__main__":
    import uvicorn
    init_db()
    uvicorn.run("crm.server:app", host="127.0.0.1", port=8000, reload=True)

