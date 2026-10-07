"""
CRM Database Layer — SQLite Engine para Gestão de Vendas, Hospedagem e MRR.

Arquitetura Industrial KONIG — Enterprise Agentic Framework.
Projetado por Bob (Arquiteto) para persistência local rápida, sem custos de cloud.
"""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


DB_PATH = Path(__file__).resolve().parent / "konig_crm.db"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Cria as tabelas do CRM caso não existam."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS deals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        instagram TEXT,
        whatsapp TEXT NOT NULL,
        niche TEXT DEFAULT 'Confeitaria Gourmet',
        specialty TEXT,
        stage TEXT NOT NULL DEFAULT 'prospeccao',
        deal_value REAL DEFAULT 699.0,
        mrr_value REAL DEFAULT 59.0,
        mrr_status TEXT DEFAULT 'pendente',
        hosting_domain TEXT,
        notes TEXT,
        created_at TEXT NOT NULL,
        closed_at TEXT,
        upsell_alert_at TEXT
    );
    """)

    # Seed com leads iniciais de confeitarias se estiver vazio
    cursor.execute("SELECT COUNT(*) as count FROM deals")
    row = cursor.fetchone()
    if row["count"] == 0:
        now = datetime.now(timezone.utc).isoformat()
        sample_deals = [
            (
                "Ateliê Doce Sabor",
                "@ateliedocesabor.oficial",
                "5511987654321",
                "Confeitaria Gourmet",
                "Bolos artísticos de pasta americana e casamentos",
                "prospeccao",
                699.0,
                59.0,
                "pendente",
                "ateliedocesabor.com.br",
                "Feed com 18k seguidores. Link na bio é um bit.ly seco pro zap. Perde muitas mensagens no fim de semana.",
                now,
                None,
                None
            ),
            (
                "Sandra Confeitaria Artesanal",
                "@sandraconfeitaria_artesanal",
                "5521998877665",
                "Confeitaria Gourmet",
                "Bolos festivos, bentô cakes e kits festa",
                "contato_enviado",
                699.0,
                79.0,
                "pendente",
                "sandrabolos.com.br",
                "Primeiro script enviado no WhatsApp. Visualizou, aguardando resposta.",
                now,
                None,
                None
            ),
            (
                "Doceria Petit Gourmet",
                "@petitgourmet_doces",
                "5531988776655",
                "Confeitaria Gourmet",
                "Doces finos para eventos e brigadeiros gourmet",
                "fechado_pago",
                699.0,
                59.0,
                "ativo",
                "petitgourmetdoces.com.br",
                "Fechou no Pix à vista! Entregue e em produção de hospedagem. Cliente quer depois lembrete de aniversários.",
                now,
                now,
                now
            )
        ]
        cursor.executemany("""
        INSERT INTO deals (
            name, instagram, whatsapp, niche, specialty, stage,
            deal_value, mrr_value, mrr_status, hosting_domain, notes,
            created_at, closed_at, upsell_alert_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, sample_deals)

    conn.commit()
    conn.close()


def list_deals() -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM deals ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_deal(deal_id: int) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM deals WHERE id = ?", (deal_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def create_deal(data: Dict[str, Any]) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.now(timezone.utc).isoformat()
    cursor.execute("""
    INSERT INTO deals (
        name, instagram, whatsapp, niche, specialty, stage,
        deal_value, mrr_value, mrr_status, hosting_domain, notes,
        created_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data.get("name"),
        data.get("instagram", ""),
        data.get("whatsapp"),
        data.get("niche", "Confeitaria Gourmet"),
        data.get("specialty", ""),
        data.get("stage", "prospeccao"),
        data.get("deal_value", 699.0),
        data.get("mrr_value", 59.0),
        data.get("mrr_status", "pendente"),
        data.get("hosting_domain", ""),
        data.get("notes", ""),
        now
    ))
    conn.commit()
    deal_id = cursor.lastrowid
    conn.close()
    return deal_id


def update_deal_stage(deal_id: int, new_stage: str) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.now(timezone.utc).isoformat()
    if new_stage in ("fechado_pago", "setup_48h", "radar_upsell"):
        cursor.execute("""
        UPDATE deals 
        SET stage = ?, 
            closed_at = COALESCE(closed_at, ?),
            mrr_status = CASE WHEN mrr_status = 'pendente' THEN 'ativo' ELSE mrr_status END
        WHERE id = ?
        """, (new_stage, now, deal_id))
    else:
        cursor.execute("UPDATE deals SET stage = ? WHERE id = ?", (new_stage, deal_id))
    conn.commit()
    updated = cursor.rowcount > 0
    conn.close()
    return updated


def get_crm_metrics() -> Dict[str, Any]:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) as total_leads FROM deals")
    total_leads = cursor.fetchone()["total_leads"]

    cursor.execute("SELECT COUNT(*) as won_count, SUM(deal_value) as won_revenue FROM deals WHERE stage IN ('fechado_pago', 'setup_48h', 'radar_upsell')")
    won_row = cursor.fetchone()
    won_count = won_row["won_count"] or 0
    won_revenue = won_row["won_revenue"] or 0.0

    cursor.execute("SELECT SUM(mrr_value) as total_mrr, COUNT(*) as active_mrr_clients FROM deals WHERE mrr_status = 'ativo'")
    mrr_row = cursor.fetchone()
    total_mrr = mrr_row["total_mrr"] or 0.0
    active_mrr_clients = mrr_row["active_mrr_clients"] or 0

    conn.close()

    return {
        "total_leads": total_leads,
        "won_count": won_count,
        "won_revenue": won_revenue,
        "total_mrr": total_mrr,
        "projected_arr": total_mrr * 12,
        "active_mrr_clients": active_mrr_clients,
        "conversion_rate": round((won_count / max(total_leads, 1)) * 100, 1)
    }
