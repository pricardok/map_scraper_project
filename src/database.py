# src/database.py
import duckdb
import pandas as pd
import os
import re
from datetime import datetime

# Template padrão de WhatsApp, usado para popular a tabela de templates.
# O markdown (negrito e links) é limpo antes do envio real no whatsapp.py.
TEMPLATE_AGRUPAMENTO_PADRAO = """Opa, tudo certo?

Conhece o **Agendamento Já**? É uma plataforma 100% online para deixar sua agenda no piloto automático e acabar com a dor de cabeça de gerenciar horários pelo WhatsApp.

Conheça nossa proposta: [https://agendamentoja.com/](https://agendamentoja.com/)
Acompanhe nosso dia a dia: [https://www.instagram.com/agendamentoja_/](https://www.instagram.com/agendamentoja_/)

Quer ver uma demonstração rápida de como funciona na prática para o seu tipo de serviço? É só me avisar!"""

class LeadDatabase:
    def __init__(self, db_path="data/leads.duckdb"):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_path = db_path
        self.conn = duckdb.connect(self.db_path)
        self._create_table()
        self._ensure_whatsapp_columns()
        self._create_templates_table()
        self._seed_templates()

    def _create_table(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS leads (
                nome VARCHAR,
                telefone VARCHAR,
                tipo_telefone VARCHAR,
                whatsapp_link VARCHAR,
                instagram VARCHAR,
                site VARCHAR,
                bairro VARCHAR,
                cidade VARCHAR,
                estado VARCHAR,
                nicho VARCHAR,
                status VARCHAR DEFAULT 'ativo',
                data_extracao TIMESTAMP,
                data_envio_whatsapp TIMESTAMP,
                status_whatsapp VARCHAR DEFAULT 'pendente',
                chat_id_waha VARCHAR,
                PRIMARY KEY (nome, cidade)
            )
        """)

    def _ensure_whatsapp_columns(self):
        """Adiciona as colunas de log de WhatsApp em bancos criados antes da migração."""
        colunas = {row[1] for row in self.conn.execute("PRAGMA table_info(leads)").fetchall()}
        if 'data_envio_whatsapp' not in colunas:
            self.conn.execute("ALTER TABLE leads ADD COLUMN data_envio_whatsapp TIMESTAMP")
        if 'status_whatsapp' not in colunas:
            self.conn.execute("ALTER TABLE leads ADD COLUMN status_whatsapp VARCHAR DEFAULT 'pendente'")
        if 'chat_id_waha' not in colunas:
            self.conn.execute("ALTER TABLE leads ADD COLUMN chat_id_waha VARCHAR")

    def _create_templates_table(self):
        """Tabela de templates de mensagem de WhatsApp (mensagem, descrição e ativo)."""
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS templates_whatsapp (
                id INTEGER PRIMARY KEY,
                mensagem VARCHAR,
                descricao VARCHAR,
                ativo BOOLEAN DEFAULT TRUE
            )
        """)

    def _seed_templates(self):
        """Garante que o template padrão do Agendamento Já exista (idempotente)."""
        self.conn.execute("""
            INSERT INTO templates_whatsapp (id, mensagem, descricao, ativo)
            SELECT 1, ?, 'Apresentação Agendamento Já', TRUE
            WHERE NOT EXISTS (SELECT 1 FROM templates_whatsapp WHERE id = 1)
        """, [TEMPLATE_AGRUPAMENTO_PADRAO])

    def listar_templates_ativos(self):
        """Retorna os templates ativos como lista de dicionários (id, mensagem, descricao, ativo)."""
        return (
            self.conn.execute("""
                SELECT id, mensagem, descricao, ativo
                FROM templates_whatsapp
                WHERE ativo = TRUE
                ORDER BY id
            """)
            .df()
            .to_dict("records")
        )

    def save_leads(self, df: pd.DataFrame):
        if df.empty:
            return 0
        
        descartados_db = self.conn.execute("SELECT nome, cidade FROM leads WHERE status = 'descartado'").fetchall()
        descartados_set = set(descartados_db)
        
        df = df[~df.apply(lambda row: (row['nome'], row['cidade']) in descartados_set, axis=1)]
        
        if df.empty:
            print("Todos os leads coletados já foram descartados anteriormente. Pulando salvamento.")
            return 0
            
        df['data_extracao'] = datetime.now()
        
        if 'status' not in df.columns:
            df['status'] = 'ativo'

        self.conn.register('df_temp', df)

        # UPSERT preservando o status atual e as colunas de log do WhatsApp.
        # Assim, re-raspar um lead já enviado NÃO apaga data_envio_whatsapp/status_whatsapp.
        self.conn.execute("""
            INSERT INTO leads (nome, telefone, tipo_telefone, whatsapp_link, instagram, site, bairro, cidade, estado, nicho, status, data_extracao)
            SELECT nome, telefone, tipo_telefone, whatsapp_link, instagram, site, bairro, cidade, estado, nicho, status, data_extracao
            FROM df_temp
            ON CONFLICT (nome, cidade) DO UPDATE SET
                telefone = excluded.telefone,
                tipo_telefone = excluded.tipo_telefone,
                whatsapp_link = excluded.whatsapp_link,
                instagram = excluded.instagram,
                site = excluded.site,
                bairro = excluded.bairro,
                estado = excluded.estado,
                nicho = excluded.nicho,
                data_extracao = excluded.data_extracao
        """)

        self.conn.unregister('df_temp')
        return len(df)

    def get_leads_para_envio(self, limite=None, numero=None, cidade=None, nicho=None):
        """Retorna leads ativos, celulares e ainda não enviados (evita spam/fixo).

        Filtros opcionais:
        - numero: filtra por telefone (completo ou parte; ignora não-dígitos)
        - cidade: filtra por nome exato da cidade
        - nicho:  filtra por nicho exato
        """
        query = """
            SELECT nome, telefone, whatsapp_link, bairro, cidade, estado, nicho, chat_id_waha
            FROM leads
            WHERE status = 'ativo'
              AND tipo_telefone = 'Celular'
              AND (status_whatsapp IS NULL OR status_whatsapp = 'pendente')
        """
        params = []
        if numero:
            numero = re.sub(r"\D", "", str(numero))
            query += " AND regexp_replace(telefone, '[^0-9]', '', 'g') LIKE ?"
            params.append(f"%{numero}%")
        if cidade:
            query += " AND cidade = ?"
            params.append(cidade)
        if nicho:
            query += " AND nicho = ?"
            params.append(nicho)
        query += " ORDER BY cidade, bairro, nome"
        if limite:
            query += " LIMIT ?"
            params.append(int(limite))
        return self.conn.execute(query, params).df()

    def salvar_chat_id_waha(self, nome, cidade, chat_id):
        """Cacheia o chatId resolvido (ex.: 143172869029943@lid) para não repetir
        a chamada ao /api/checkNumberStatus em envios futuros."""
        self.conn.execute("""
            UPDATE leads
            SET chat_id_waha = ?
            WHERE nome = ? AND cidade = ?
        """, [chat_id, nome, cidade])

    def marcar_envio(self, nome, cidade, status_whatsapp):
        """Registra o resultado do envio. 'data_envio_whatsapp' é gravado apenas no sucesso."""
        if status_whatsapp == 'enviado':
            self.conn.execute("""
                UPDATE leads
                SET status_whatsapp = ?, data_envio_whatsapp = ?
                WHERE nome = ? AND cidade = ?
            """, [status_whatsapp, datetime.now(), nome, cidade])
        else:
            self.conn.execute("""
                UPDATE leads
                SET status_whatsapp = ?
                WHERE nome = ? AND cidade = ?
            """, [status_whatsapp, nome, cidade])

    def export_to_excel(self, nicho: str, cidade: str):
        df = self.conn.execute("""
            SELECT nome, telefone, tipo_telefone, whatsapp_link, instagram, site, bairro, data_extracao 
            FROM leads 
            WHERE nicho = ? AND cidade = ? AND status = 'ativo'
            ORDER BY bairro, nome
        """, [nicho, cidade]).df()
        
        if df.empty:
            print("Nenhum dado ativo para exportar.")
            return
            
        os.makedirs("output", exist_ok=True)
        nome_arquivo = f"output/leads_{nicho}_{cidade}.xlsx".replace(" ", "_").lower()
        df.to_excel(nome_arquivo, index=False)
        print(f"🎉 Exportação concluída: {nome_arquivo} ({len(df)} leads ativos)")

    def close(self):
        self.conn.close()