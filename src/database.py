# src/database.py
"""Camada de acesso a dados (leads, templates e log de envio).

Usa `src/backend.py`, que abstrai PostgreSQL e DuckDB — o código daqui não
depende do banco específico. A criação do schema e o seed dos templates ficam
em `src/schema.py` (executado uma vez no setup: `python src/schema.py`).
"""
import os
import re
import json
from datetime import datetime

import pandas as pd

from src import backend


class LeadDatabase:
    def __init__(self, conn=None):
        self.conn = conn if conn is not None else backend.conectar()

    def listar_templates_ativos(self):
        """Retorna os templates ativos como lista de dicionários (id, mensagem, descricao, segmento, ativo)."""
        return (
            backend.query_df(self.conn, """
                SELECT id, mensagem, descricao, segmento, ativo
                FROM templates_whatsapp
                WHERE ativo = TRUE
                ORDER BY id
            """)
            .to_dict("records")
        )

    def salvar_log_envio(self, lead_id, nome, cidade, telefone, chat_id, status,
                         mensagem=None, payload=None, erro=None):
        """Grava uma linha de log de envio com os campos normalizados.

        - `lead_id`: referencia `leads.lead_id` (vínculo por PK).
        - `telefone` é reduzido a dígitos (mesma representação de `leads.telefone`),
          permitindo JOIN direto: leads.telefone = whatsapp_envios_log.telefone.
        """
        telefone = re.sub(r"\D", "", str(telefone or ""))
        telefone_normalizado = None
        if telefone.startswith("55") and len(telefone) > 11:
            base = telefone[2:]
        else:
            base = telefone
        if len(base) == 11:
            telefone_normalizado = f"55{base}"
        elif telefone:
            telefone_normalizado = telefone

        payload_str = None
        if payload is not None:
            if isinstance(payload, (dict, list)):
                try:
                    payload_str = json.dumps(payload, ensure_ascii=False, default=str)
                except Exception:
                    payload_str = str(payload)
            else:
                payload_str = str(payload)

        p = backend.ph()
        backend.execute(self.conn, f"""
            INSERT INTO whatsapp_envios_log
                (lead_id, nome, cidade, telefone, telefone_normalizado, chat_id,
                 status, mensagem, payload, erro, data_envio)
            VALUES ({p}, {p}, {p}, {p}, {p}, {p}, {p}, {p}, {p}, {p}, {p})
        """, [
            lead_id, nome, cidade, telefone or None, telefone_normalizado, chat_id,
            status, mensagem, payload_str, erro, datetime.now(),
        ])
        backend.commit(self.conn)

    def save_leads(self, df: pd.DataFrame):
        if df.empty:
            return 0

        descartados = set(backend.query_all(
            self.conn, "SELECT nome, cidade FROM leads WHERE status = 'descartado'"
        ))
        df = df[~df.apply(lambda row: (row['nome'], row['cidade']) in descartados, axis=1)]

        if df.empty:
            print("Todos os leads coletados já foram descartados anteriormente. Pulando salvamento.")
            return 0

        df = df.copy()
        df['data_extracao'] = datetime.now()
        if 'status' not in df.columns:
            df['status'] = 'ativo'

        colunas = [
            'nome', 'telefone', 'tipo_telefone', 'whatsapp_link', 'instagram',
            'site', 'bairro', 'cidade', 'estado', 'nicho', 'status', 'data_extracao',
        ]
        linhas = [
            tuple(backend._valor(r.get(c)) for c in colunas)
            for r in df.to_dict("records")
        ]

        # UPSERT preservando o status atual e as colunas de log do WhatsApp.
        # Assim, re-raspar um lead já enviado NÃO apaga data_envio_whatsapp/status_whatsapp.
        backend.bulk_upsert(
            self.conn,
            table="leads",
            columns=colunas,
            rows=linhas,
            conflict="nome, cidade",
            set_clause=(
                "telefone = excluded.telefone, "
                "tipo_telefone = excluded.tipo_telefone, "
                "whatsapp_link = excluded.whatsapp_link, "
                "instagram = excluded.instagram, "
                "site = excluded.site, "
                "bairro = excluded.bairro, "
                "estado = excluded.estado, "
                "nicho = excluded.nicho, "
                "data_extracao = excluded.data_extracao"
            ),
        )
        backend.commit(self.conn)
        return len(df)

    def get_leads_para_envio(self, limite=None, numero=None, cidade=None, nicho=None):
        """Retorna leads ativos, celulares e ainda não enviados (evita spam/fixo).

        Filtros opcionais:
        - numero: filtra por telefone (completo ou parte; ignora não-dígitos)
        - cidade: filtra por nome exato da cidade
        - nicho:  filtra por nicho exato
        """
        p = backend.ph()
        query = f"""
            SELECT lead_id, nome, telefone, whatsapp_link, bairro, cidade, estado, nicho, chat_id_waha
            FROM leads
            WHERE status = 'ativo'
              AND tipo_telefone = 'Celular'
              AND (status_whatsapp IS NULL OR status_whatsapp = 'pendente')
        """
        params = []
        if numero:
            numero = re.sub(r"\D", "", str(numero))
            query += f" AND regexp_replace(telefone, '[^0-9]', '', 'g') LIKE {p}"
            params.append(f"%{numero}%")
        if cidade:
            query += f" AND cidade = {p}"
            params.append(cidade)
        if nicho:
            query += f" AND nicho = {p}"
            params.append(nicho)
        query += " ORDER BY cidade, bairro, nome"
        if limite:
            query += f" LIMIT {p}"
            params.append(int(limite))
        return backend.query_df(self.conn, query, params)

    def salvar_chat_id_waha(self, nome, cidade, chat_id):
        """Cacheia o chatId resolvido (ex.: 143172869029943@lid) para não repetir
        a chamada ao /api/checkNumberStatus em envios futuros."""
        p = backend.ph()
        backend.execute(self.conn, f"""
            UPDATE leads
            SET chat_id_waha = {p}
            WHERE nome = {p} AND cidade = {p}
        """, [chat_id, nome, cidade])
        backend.commit(self.conn)

    def marcar_envio(self, nome, cidade, status_whatsapp):
        """Registra o resultado do envio. 'data_envio_whatsapp' é gravado apenas no sucesso."""
        p = backend.ph()
        if status_whatsapp == 'enviado':
            backend.execute(self.conn, f"""
                UPDATE leads
                SET status_whatsapp = {p}, data_envio_whatsapp = {p}
                WHERE nome = {p} AND cidade = {p}
            """, [status_whatsapp, datetime.now(), nome, cidade])
        else:
            backend.execute(self.conn, f"""
                UPDATE leads
                SET status_whatsapp = {p}
                WHERE nome = {p} AND cidade = {p}
            """, [status_whatsapp, nome, cidade])
        backend.commit(self.conn)

    def export_to_excel(self, nicho: str, cidade: str):
        p = backend.ph()
        df = backend.query_df(self.conn, f"""
            SELECT nome, telefone, tipo_telefone, whatsapp_link, instagram, site, bairro, data_extracao
            FROM leads
            WHERE nicho = {p} AND cidade = {p} AND status = 'ativo'
            ORDER BY bairro, nome
        """, [nicho, cidade])

        if df.empty:
            print("Nenhum dado ativo para exportar.")
            return

        os.makedirs("output", exist_ok=True)
        nome_arquivo = f"output/leads_{nicho}_{cidade}.xlsx".replace(" ", "_").lower()
        df.to_excel(nome_arquivo, index=False)
        print(f"🎉 Exportação concluída: {nome_arquivo} ({len(df)} leads ativos)")

    def close(self):
        backend.close(self.conn)
