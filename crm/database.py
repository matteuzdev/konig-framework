"""
CRM Database Layer — SQLite Engine para Gestão de Vendas, Hospedagem e MRR.

Arquitetura Industrial KONIG — Enterprise Agentic Framework.
Projetado por Bob (Arquiteto) com suporte a Ficha Completa do Negócio e Google Meu Negócio (GMB).
"""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

DB_PATH = Path(__file__).resolve().parent / "konig_crm.db"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def ensure_columns(cursor: sqlite3.Cursor) -> None:
    """Migração idempotente para adicionar campos ricos de GMB e Ficha do Lead."""
    cursor.execute("PRAGMA table_info(deals)")
    existing_cols = {r["name"] for r in cursor.fetchall()}

    new_cols = {
        "owner_name": "TEXT DEFAULT ''",
        "city_state": "TEXT DEFAULT ''",
        "gmb_rating": "REAL DEFAULT 4.9",
        "gmb_reviews_count": "INTEGER DEFAULT 85",
        "gmb_url": "TEXT DEFAULT ''",
        "gmb_top_review": "TEXT DEFAULT ''",
        "bio_link_type": "TEXT DEFAULT 'Linktree confuso'",
    }

    for col_name, col_def in new_cols.items():
        if col_name not in existing_cols:
            cursor.execute(f"ALTER TABLE deals ADD COLUMN {col_name} {col_def}")


def init_db() -> None:
    """Cria as tabelas do CRM caso não existam e executa migrações necessárias."""
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

    ensure_columns(cursor)

    # Verifica se já temos dados ou se precisa popular
    cursor.execute("SELECT COUNT(*) as count FROM deals")
    count = cursor.fetchone()["count"]

    if count == 0:
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
                None,
                "Camila",
                "Vila Mariana, São Paulo - SP",
                4.9,
                142,
                "https://maps.google.com/?q=Atelie+Doce+Sabor",
                "Bolo de casamento dos sonhos! Todos os convidados elogiaram a massa fofinha e o recheio de pistache. Entrega pontual impecável.",
                "Linktree confuso com 8 botões"
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
                None,
                "Sandra",
                "Tijuca, Rio de Janeiro - RJ",
                4.8,
                98,
                "https://maps.google.com/?q=Sandra+Confeitaria+Artesanal",
                "Os bentô cakes da Sandra salvam qualquer comemoração de última hora! Super caprichosa e sabor maravilhoso.",
                "Link seco do WhatsApp sem catálogo"
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
                now,
                "Patrícia",
                "Lourdes, Belo Horizonte - MG",
                5.0,
                215,
                "https://maps.google.com/?q=Doceria+Petit+Gourmet",
                "Melhor confeitaria fina de BH disparado. Os brigadeiros gourmet belgas e doces finos para casamento são de outro mundo.",
                "Site no ar com cardápio interativo"
            )
        ]
        cursor.executemany("""
        INSERT INTO deals (
            name, instagram, whatsapp, niche, specialty, stage,
            deal_value, mrr_value, mrr_status, hosting_domain, notes,
            created_at, closed_at, upsell_alert_at,
            owner_name, city_state, gmb_rating, gmb_reviews_count, gmb_url, gmb_top_review, bio_link_type
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, sample_deals)
    else:
        # Atualiza leads existentes com dados ricos de exemplo caso estejam vazios
        cursor.execute("""
        UPDATE deals 
        SET owner_name = 'Sandra',
            city_state = 'Tijuca, Rio de Janeiro - RJ',
            gmb_rating = 4.8,
            gmb_reviews_count = 98,
            gmb_top_review = 'Os bentô cakes da Sandra salvam qualquer comemoração de última hora! Super caprichosa e sabor maravilhoso.',
            bio_link_type = 'Link seco do WhatsApp sem catálogo'
        WHERE name LIKE '%Sandra%' AND (owner_name IS NULL OR owner_name = '')
        """)
        cursor.execute("""
        UPDATE deals 
        SET owner_name = 'Camila',
            city_state = 'Vila Mariana, São Paulo - SP',
            gmb_rating = 4.9,
            gmb_reviews_count = 142,
            gmb_top_review = 'Bolo de casamento dos sonhos! Todos os convidados elogiaram a massa fofinha e o recheio de pistache. Entrega pontual impecável.',
            bio_link_type = 'Linktree confuso com 8 botões'
        WHERE name LIKE '%Doce Sabor%' AND (owner_name IS NULL OR owner_name = '')
        """)
        cursor.execute("""
        UPDATE deals 
        SET owner_name = 'Patrícia',
            city_state = 'Lourdes, Belo Horizonte - MG',
            gmb_rating = 5.0,
            gmb_reviews_count = 215,
            gmb_top_review = 'Melhor confeitaria fina de BH disparado. Os brigadeiros gourmet belgas e doces finos para casamento são de outro mundo.',
            bio_link_type = 'Site no ar com cardápio interativo'
        WHERE name LIKE '%Petit%' AND (owner_name IS NULL OR owner_name = '')
        """)

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
        created_at,
        owner_name, city_state, gmb_rating, gmb_reviews_count, gmb_url, gmb_top_review, bio_link_type
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
        now,
        data.get("owner_name", ""),
        data.get("city_state", ""),
        data.get("gmb_rating", 4.9),
        data.get("gmb_reviews_count", 0),
        data.get("gmb_url", ""),
        data.get("gmb_top_review", ""),
        data.get("bio_link_type", "Linktree confuso")
    ))
    conn.commit()
    deal_id = cursor.lastrowid
    conn.close()
    return deal_id


def update_deal(deal_id: int, data: Dict[str, Any]) -> bool:
    """Atualiza dados cadastrais e de inteligência da Ficha do Lead."""
    conn = get_connection()
    cursor = conn.cursor()

    fields = [
        "name", "owner_name", "city_state", "instagram", "whatsapp",
        "specialty", "deal_value", "mrr_value", "hosting_domain", "notes",
        "gmb_rating", "gmb_reviews_count", "gmb_url", "gmb_top_review", "bio_link_type"
    ]

    updates = []
    values = []
    for f in fields:
        if f in data:
            updates.append(f"{f} = ?")
            values.append(data[f])

    if not updates:
        conn.close()
        return False

    values.append(deal_id)
    query = f"UPDATE deals SET {', '.join(updates)} WHERE id = ?"
    cursor.execute(query, values)
    conn.commit()
    updated = cursor.rowcount > 0
    conn.close()
    return updated


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
