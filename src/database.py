# src/database.py
import duckdb
import pandas as pd
import os
from datetime import datetime

class LeadDatabase:
    def __init__(self, db_path="data/leads.duckdb"):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_path = db_path
        self.conn = duckdb.connect(self.db_path)
        self._create_table()
        self._ensure_whatsapp_columns()

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

    def get_leads_para_envio(self, limite=None):
        """Retorna leads ativos, celulares e ainda não enviados (evita spam/fixo)."""
        query = """
            SELECT nome, telefone, whatsapp_link, bairro, cidade, estado, nicho
            FROM leads
            WHERE status = 'ativo'
              AND tipo_telefone = 'Celular'
              AND (status_whatsapp IS NULL OR status_whatsapp = 'pendente')
            ORDER BY cidade, bairro, nome
        """
        if limite:
            query += f" LIMIT {int(limite)}"
        return self.conn.execute(query).df()

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