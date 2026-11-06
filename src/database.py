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
        self._progresso_pronto = False

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
        """Retorna leads ativos, celulares e ainda não enviados.

        Filtros opcionais:
        - numero: filtra por telefone (completo ou parte; ignora não-dígitos)
        - cidade: filtra por nome exato da cidade
        - nicho:  filtra por nicho exato

        ⚠️ DEDUPLICAÇÃO POR TELEFONE (importante para custo e anti-spam)
        ---------------------------------------------------------------
        A base tem o mesmo telefone em VÁRIAS linhas:

        - Redes com filiais que compartilham o número (ex.: 4 unidades da
          mesma barbearia em Niterói com o mesmo celular);
        - O mesmo negócio raspado em dezenas de cidades diferentes
          (medido: um número aparecia em 56 cidades).

        Sem deduplicar, cada linha vira uma mensagem cobrada — e o dono do
        número recebe a mesma campanha várias vezes, o que gera denúncia de
        spam e derruba a qualidade do número oficial.

        Regra aplicada:
          1. UMA linha por telefone (DISTINCT ON);
          2. exclui telefones que JÁ receberam envio com sucesso em QUALQUER
             campanha anterior (independente de cidade/nicho/bairro).

        A fonte de verdade do "já enviado" é `whatsapp_envios_log` (status
        'enviado'), não `leads.status_whatsapp` — porque a marcação no lead
        pode falhar ou ser feita em outra linha do mesmo telefone.
        """
        p = backend.ph()
        expr_tel = "regexp_replace(COALESCE(l.telefone, ''), '[^0-9]', '', 'g')"

        # Subconsulta: telefones já enviados com sucesso (1 linha por número).
        sub_ja_enviados = f"""
            SELECT DISTINCT regexp_replace(COALESCE(telefone, ''), '[^0-9]', '', 'g') AS tel
            FROM whatsapp_envios_log
            WHERE status = 'enviado'
        """

        query = f"""
            SELECT DISTINCT ON ({expr_tel})
                   l.lead_id, l.nome, l.telefone, l.whatsapp_link,
                   l.bairro, l.cidade, l.estado, l.nicho, l.chat_id_waha
            FROM leads l
            WHERE l.status = 'ativo'
              AND l.tipo_telefone = 'Celular'
              AND (l.status_whatsapp IS NULL OR l.status_whatsapp = 'pendente')
              AND {expr_tel} <> ''
              AND {expr_tel} NOT IN ({sub_ja_enviados})
        """
        params = []
        if numero:
            numero = re.sub(r"\D", "", str(numero))
            query += f" AND {expr_tel} LIKE {p}"
            params.append(f"%{numero}%")
        if cidade:
            query += f" AND l.cidade = {p}"
            params.append(cidade)
        if nicho:
            query += f" AND l.nicho = {p}"
            params.append(nicho)

        # DISTINCT ON exige que a ordem comece pela expressão do DISTINCT.
        # Dentro de cada telefone, escolhe a linha mais estável (lead_id).
        query += f" ORDER BY {expr_tel}, l.lead_id"

        # O LIMIT precisa ser aplicado DEPOIS da deduplicação — por isso
        # envolvemos em um SELECT externo.
        if limite:
            query = f"SELECT * FROM ({query}) AS dedup LIMIT {p}"
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

    def marcar_envio(self, nome, cidade, status_whatsapp, lead_id=None, telefone=None):
        """Registra o resultado do envio.

        'data_envio_whatsapp' é gravado apenas no sucesso.

        ⚠️ IDENTIFICAÇÃO DA LINHA (ordem de preferência)
        ------------------------------------------------
        1. `lead_id`    → chave primária, sempre correta
        2. `telefone`   → marca TODAS as linhas com aquele número, o que é
                          exatamente o desejado quando o mesmo celular aparece
                          em várias linhas (redes com filiais, mesmo negócio
                          raspado em cidades diferentes). Assim o número não
                          volta na próxima campanha por outra linha.
        3. nome+cidade  → legado; usado só quando nada mais é informado.

        O `WHERE nome = ? AND cidade = ?` sozinho era frágil: não cobria o
        mesmo telefone em outra cidade, então a campanha seguinte reenviava
        para um número que já havia recebido a mensagem.
        """
        p = backend.ph()

        if lead_id is not None:
            where = f"lead_id = {p}"
            params_where = [lead_id]
        elif telefone:
            digitos = re.sub(r"\D", "", str(telefone))
            if not digitos:
                print("Aviso: marcar_envio sem telefone válido — usando nome+cidade.")
                where = f"nome = {p} AND cidade = {p}"
                params_where = [nome, cidade]
            else:
                where = (f"regexp_replace(COALESCE(telefone, ''), '[^0-9]', '', 'g') = {p}")
                params_where = [digitos]
        else:
            where = f"nome = {p} AND cidade = {p}"
            params_where = [nome, cidade]

        if status_whatsapp == 'enviado':
            backend.execute(self.conn, f"""
                UPDATE leads
                SET status_whatsapp = {p}, data_envio_whatsapp = {p}
                WHERE {where}
            """, [status_whatsapp, datetime.now()] + params_where)
        else:
            backend.execute(self.conn, f"""
                UPDATE leads
                SET status_whatsapp = {p}
                WHERE {where}
            """, [status_whatsapp] + params_where)
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

    # ------------------------------------------------------------------
    # Progresso da coleta (permite retomar de onde parou)
    # ------------------------------------------------------------------
    def _garantir_tabela_progresso(self):
        """Cria `coleta_progresso` na primeira utilização (idempotente)."""
        if self._progresso_pronto:
            return

        tipo = "VARCHAR" if backend.IS_DUCKDB else "TEXT"
        backend.execute(self.conn, f"""
            CREATE TABLE IF NOT EXISTS coleta_progresso (
                nicho {tipo} NOT NULL,
                uf {tipo} NOT NULL,
                cidade {tipo} NOT NULL,
                status {tipo} NOT NULL DEFAULT 'pendente',
                termos_total INTEGER,
                leads_total INTEGER,
                tentativas INTEGER DEFAULT 0,
                erro {tipo},
                iniciado_em TIMESTAMP,
                atualizado_em TIMESTAMP,
                concluido_em TIMESTAMP,
                PRIMARY KEY (nicho, uf, cidade)
            )
        """)
        backend.commit(self.conn)
        self._progresso_pronto = True

    def progresso_carregar(self, nicho):
        """Retorna {(uf, cidade): {status, tentativas, leads_total, concluido_em}}."""
        self._garantir_tabela_progresso()
        p = backend.ph()
        linhas = backend.query_all(self.conn, f"""
            SELECT uf, cidade, status, tentativas, leads_total, concluido_em
            FROM coleta_progresso
            WHERE nicho = {p}
        """, [nicho])
        return {
            (uf, cidade): {
                "status": status,
                "tentativas": tentativas or 0,
                "leads_total": leads_total or 0,
                "concluido_em": concluido_em,
            }
            for uf, cidade, status, tentativas, leads_total, concluido_em in linhas
        }

    def progresso_iniciar(self, nicho, uf, cidade, termos_total):
        """Marca a cidade como em andamento (incrementa o contador de tentativas)."""
        self._garantir_tabela_progresso()
        p = backend.ph()
        linha = backend.query_one(self.conn, f"""
            SELECT tentativas FROM coleta_progresso
            WHERE nicho = {p} AND uf = {p} AND cidade = {p}
        """, [nicho, uf, cidade])
        tentativas = (int(linha[0] or 0) if linha else 0) + 1
        agora = datetime.now()
        backend.execute(self.conn, f"""
            INSERT INTO coleta_progresso
                (nicho, uf, cidade, status, termos_total, tentativas,
                 erro, iniciado_em, atualizado_em, concluido_em)
            VALUES ({p}, {p}, {p}, {p}, {p}, {p}, NULL, {p}, {p}, NULL)
            ON CONFLICT (nicho, uf, cidade) DO UPDATE SET
                status = excluded.status,
                termos_total = excluded.termos_total,
                tentativas = excluded.tentativas,
                erro = NULL,
                iniciado_em = excluded.iniciado_em,
                atualizado_em = excluded.atualizado_em,
                concluido_em = NULL
        """, [nicho, uf, cidade, "em_andamento", int(termos_total), tentativas, agora, agora])
        backend.commit(self.conn)

    def progresso_concluir(self, nicho, uf, cidade, leads_total=0):
        """Marca a cidade como concluída."""
        self._garantir_tabela_progresso()
        p = backend.ph()
        agora = datetime.now()
        backend.execute(self.conn, f"""
            UPDATE coleta_progresso
            SET status = {p}, leads_total = {p}, erro = NULL,
                atualizado_em = {p}, concluido_em = {p}
            WHERE nicho = {p} AND uf = {p} AND cidade = {p}
        """, ["concluida", int(leads_total or 0), agora, agora, nicho, uf, cidade])
        backend.commit(self.conn)

    def progresso_erro(self, nicho, uf, cidade, erro):
        """Registra a falha da cidade (será tentada novamente no próximo ciclo)."""
        self._garantir_tabela_progresso()
        p = backend.ph()
        backend.execute(self.conn, f"""
            UPDATE coleta_progresso
            SET status = {p}, erro = {p}, atualizado_em = {p}
            WHERE nicho = {p} AND uf = {p} AND cidade = {p}
        """, ["erro", str(erro)[:500], datetime.now(), nicho, uf, cidade])
        backend.commit(self.conn)

    def progresso_parcial(self, nicho, uf, cidade, leads_total, motivo):
        """Cidade coletada em parte (bloqueio/timeout em alguma área).

        Fica fora do filtro de "concluída" para ser tentada de novo no próximo
        ciclo, sem perder os leads já gravados.
        """
        self._garantir_tabela_progresso()
        p = backend.ph()
        backend.execute(self.conn, f"""
            UPDATE coleta_progresso
            SET status = {p}, leads_total = {p}, erro = {p}, atualizado_em = {p}
            WHERE nicho = {p} AND uf = {p} AND cidade = {p}
        """, ["parcial", int(leads_total or 0), str(motivo)[:500], datetime.now(),
              nicho, uf, cidade])
        backend.commit(self.conn)

    def semear_progresso_de_leads(self, nicho):
        """Marca como concluídas as cidades que já possuem leads no banco.

        Serve para retomar a partir de uma coleta que rodou antes de existir o
        progresso. É idempotente e nunca sobrescreve um registro já existente.
        Retorna quantas cidades foram marcadas.
        """
        self._garantir_tabela_progresso()
        p = backend.ph()
        linhas = backend.query_all(self.conn, f"""
            SELECT estado, cidade, COUNT(*) AS total, MAX(data_extracao) AS ultima
            FROM leads
            WHERE nicho = {p} AND estado IS NOT NULL AND cidade IS NOT NULL
            GROUP BY estado, cidade
        """, [nicho])

        agora = datetime.now()
        for uf, cidade, total, ultima in linhas:
            backend.execute(self.conn, f"""
                INSERT INTO coleta_progresso
                    (nicho, uf, cidade, status, leads_total, tentativas,
                     iniciado_em, atualizado_em, concluido_em)
                VALUES ({p}, {p}, {p}, {p}, {p}, 1, {p}, {p}, {p})
                ON CONFLICT (nicho, uf, cidade) DO NOTHING
            """, [
                nicho, uf, cidade, "concluida", int(total or 0),
                ultima or agora, ultima or agora, ultima or agora,
            ])
        backend.commit(self.conn)
        return len(linhas)

    def close(self):
        backend.close(self.conn)
