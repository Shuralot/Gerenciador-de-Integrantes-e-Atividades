import sqlite3
import sys
import os
import uuid


class DatabaseManager:
    def __init__(self, db_name="dados_app.db"):
        self.db_name = db_name
        self.conn = None
        self.cursor = None
        self.connect()
        self.initialize_tables()

    def get_db_path(self):
        """Garante que o banco seja salvo ao lado do .exe ou do script."""
        if getattr(sys, 'frozen', False):
            application_path = os.path.dirname(sys.executable)
        else:
            application_path = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(application_path, self.db_name)

    def connect(self):
        try:
            self.conn = sqlite3.connect(self.get_db_path())
            self.conn.row_factory = sqlite3.Row
            self.cursor = self.conn.cursor()
            self.cursor.execute("PRAGMA foreign_keys = ON;")
        except sqlite3.Error as e:
            print(f"Erro ao conectar ao DB: {e}")

    def initialize_tables(self):
        """Cria as tabelas necessárias para o app.

        Tabelas:
        - integrantes: id, nome, funcao, data_cadastro
        - atividades: id, uuid, atividade, status, data_criacao
        - atividade_responsaveis: id, atividade_id, integrante_id
        - logs: id, acao, data
        """
        sql_integrantes = """
        CREATE TABLE IF NOT EXISTS integrantes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            funcao TEXT,
            data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """

        sql_atividades = """
        CREATE TABLE IF NOT EXISTS atividades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            uuid TEXT UNIQUE,
            atividade TEXT NOT NULL,
            status TEXT,
            data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """

        sql_atividade_responsaveis = """
        CREATE TABLE IF NOT EXISTS atividade_responsaveis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            atividade_id INTEGER NOT NULL,
            integrante_id INTEGER NOT NULL,
            FOREIGN KEY (atividade_id) REFERENCES atividades(id) ON DELETE CASCADE,
            FOREIGN KEY (integrante_id) REFERENCES integrantes(id) ON DELETE CASCADE
        );
        """

        sql_logs = """
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            acao TEXT,
            data TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """

        self.cursor.execute(sql_integrantes)
        self.cursor.execute(sql_atividades)
        self.cursor.execute(sql_atividade_responsaveis)
        self.cursor.execute(sql_logs)
        self.conn.commit()

    # --- Integrantes ---
    def add_integrante(self, nome, funcao=None):
        try:
            self.cursor.execute("INSERT INTO integrantes (nome, funcao) VALUES (?, ?)", (nome, funcao))
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Erro ao inserir integrante: {e}")
            return None

    def delete_integrante(self, integrante_id):
        """Remove um integrante pelo id. Retorna True/False."""
        try:
            self.cursor.execute("DELETE FROM integrantes WHERE id = ?", (integrante_id,))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Erro ao remover integrante: {e}")
            return False

    def delete_atividade(self, atividade_id):
        """Remove uma atividade pelo id (cascade remove responsaveis)."""
        try:
            self.cursor.execute("DELETE FROM atividades WHERE id = ?", (atividade_id,))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Erro ao remover atividade: {e}")
            return False

    def listar_integrantes(self):
        """Retorna lista de dicionários: [{'id','nome','funcao'}, ...]"""
        self.cursor.execute("SELECT id, nome, funcao FROM integrantes ORDER BY nome")
        rows = self.cursor.fetchall()
        return [dict(r) for r in rows]

    # compatibility alias
    def listar_usuarios(self):
        return self.listar_integrantes()

    # --- Atividades ---
    def add_atividade(self, atividade, status, responsaveis_ids):
        """Adiciona atividade e associa os responsáveis (lista de integrante ids)."""
        try:
            uid = str(uuid.uuid4())
            self.cursor.execute("INSERT INTO atividades (uuid, atividade, status) VALUES (?, ?, ?)",
                                (uid, atividade, status))
            atividade_id = self.cursor.lastrowid

            for integrante_id in responsaveis_ids:
                self.cursor.execute(
                    "INSERT INTO atividade_responsaveis (atividade_id, integrante_id) VALUES (?, ?)",
                    (atividade_id, integrante_id)
                )

            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Erro ao adicionar atividade: {e}")
            return False

    def get_atividades(self):
        """Retorna lista de atividades com os responsáveis embutidos.

        Cada item: {id, uuid, atividade, status, responsaveis: [{'id','nome','funcao'}, ...]}
        """
        sql = """
        SELECT a.id as atividade_id, a.uuid, a.atividade, a.status,
               i.id as integrante_id, i.nome, i.funcao
        FROM atividades a
        LEFT JOIN atividade_responsaveis ar ON ar.atividade_id = a.id
        LEFT JOIN integrantes i ON i.id = ar.integrante_id
        ORDER BY a.id;
        """

        self.cursor.execute(sql)
        rows = self.cursor.fetchall()

        atividades = {}
        for r in rows:
            aid = r['atividade_id']
            if aid not in atividades:
                atividades[aid] = {
                    'id': aid,
                    'uuid': r['uuid'],
                    'atividade': r['atividade'],
                    'status': (r['status'] or '').lower(),
                    'responsaveis': []
                }

            if r['integrante_id'] is not None:
                atividades[aid]['responsaveis'].append({
                    'id': r['integrante_id'],
                    'nome': r['nome'],
                    'funcao': r['funcao']
                })

        return list(atividades.values())

    # --- Logs e utilitários ---
    def add_log(self, acao):
        try:
            self.cursor.execute("INSERT INTO logs (acao) VALUES (?)", (acao,))
            self.conn.commit()
        except sqlite3.Error:
            pass

    def fechar(self):
        if self.conn:
            self.conn.close()