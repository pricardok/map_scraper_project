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

    def _create_table(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS leads (
                nome VARCHAR,
                telefone VARCHAR,
                tipo_telefone VARCHAR,
                whatsapp_link VARCHAR, -- NOVA COLUNA
                instagram VARCHAR,
                site VARCHAR,
                bairro VARCHAR,
                cidade VARCHAR,
                estado VARCHAR,
                nicho VARCHAR,
                status VARCHAR DEFAULT 'ativo',
                data_extracao TIMESTAMP,
                PRIMARY KEY (nome, cidade)
            )
        """)

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
        
        # Atualizado para incluir whatsapp_link
        self.conn.execute("""
            INSERT OR REPLACE INTO leads (nome, telefone, tipo_telefone, whatsapp_link, instagram, site, bairro, cidade, estado, nicho, status, data_extracao)
            SELECT nome, telefone, tipo_telefone, whatsapp_link, instagram, site, bairro, cidade, estado, nicho, status, data_extracao
            FROM df_temp
        """)
        
        self.conn.unregister('df_temp')
        return len(df)

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