"""
Suíte de Homologação & QA do KONIG Sales, Hosting & MRR CRM.

Elaborado por Elena (Staff QA & Test Automation Engineer).
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from crm.database import init_db, list_deals, get_crm_metrics
from crm.server import app

client = TestClient(app)


def test_crm_database_initialization():
    """Valida se o banco SQLite inicializa com os leads pré-carregados de confeitaria."""
    init_db()
    deals = list_deals()
    assert len(deals) >= 3, "Deveria conter pelo menos 3 leads de exemplo"
    assert any("Confeitaria" in d["name"] or "Doceria" in d["name"] for d in deals)


def test_crm_dashboard_html():
    """Valida se a interface Kanban HTML responsiva é servida corretamente."""
    response = client.get("/")
    assert response.status_code == 200
    assert "KONIG Pipeline CRM" in response.text
    assert "MRR de Hospedagem" in response.text
    assert "Radar LTV (Jay Abraham)" in response.text


def test_crm_api_metrics():
    """Valida os cálculos de faturamento front-end, MRR e ARR."""
    response = client.get("/api/metrics")
    assert response.status_code == 200
    data = response.json()
    assert "won_revenue" in data
    assert "total_mrr" in data
    assert "projected_arr" in data
    assert data["won_revenue"] >= 699.0
    assert data["total_mrr"] >= 59.0
    assert data["projected_arr"] == data["total_mrr"] * 12


def test_crm_create_deal_and_move_stage():
    """Valida a criação de um novo lead de confeitaria e o avanço no funil Kanban."""
    new_lead = {
        "name": "Doces da Vovó Maria",
        "instagram": "@docesdavovomaria",
        "whatsapp": "5511998877112",
        "niche": "Confeitaria Gourmet",
        "specialty": "Tortas artesanais e bolos vulcão",
        "deal_value": 699.0,
        "mrr_value": 79.0,
        "notes": "Bio com link quebrado. Pronta para fechar."
    }
    create_res = client.post("/api/deals", json=new_lead)
    assert create_res.status_code == 200
    deal_id = create_res.json()["id"]

    # Move para 'fechado_pago'
    move_res = client.patch(f"/api/deals/{deal_id}/stage", json={"stage": "fechado_pago"})
    assert move_res.status_code == 200

    # Verifica métricas atualizadas
    metrics_res = client.get("/api/metrics")
    data = metrics_res.json()
    assert data["won_revenue"] >= 1398.0  # Pelo menos 2 deals fechados


def test_crm_jay_abraham_upsell_script():
    """Valida se o gerador de scripts de upsell do Jay Abraham monta a abordagem de forma contextual."""
    deals = list_deals()
    first_deal = deals[0]
    res = client.get(f"/api/upsell-script/{first_deal['id']}")
    assert res.status_code == 200
    data = res.json()
    assert "Lembrete Automático" in data["upsell_name"]
    assert "hospedagem" in data["script"]
