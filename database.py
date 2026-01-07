import sqlite3
import sys
import os

class DatabaseManager:
    def __init__(self, db_name="dados_app.db"):
        self.db_name = db_name
        self.conn = None
        self.cursor = None
        self.connect()
        self.initialize_tables() # Cria as tabelas se não existirem

    def get_db_path(self):
        """ Garante que o banco seja salvo ao lado do .exe """
        if getattr(sys, 'frozen', False):
            # Se for executável
            application_path = os.path.dirname(sys.executable)
        else:
            # Se for script python normal
            application_path = os.path.dirname(os.path.abspath(__file__))
        
        return os.path.join(application_path, self.db_name)

    def connect(self):
        try:
            self.conn = sqlite3.connect(self.get_db_path())
            self.cursor = self.conn.cursor()
            # Habilita chaves estrangeiras (opcional, mas recomendado)
            self.cursor.execute("PRAGMA foreign_keys = ON;")
        except sqlite3.Error as e:
            print(f"Erro ao conectar: {e}")

    def initialize_tables(self):
        """ Defina aqui a estrutura do seu banco (o Schema) """
        # Exemplo: Tabela de Configurações ou Usuários
        sql_create_users = """
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT UNIQUE,
            data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        # Você pode ter várias tabelas
        sql_create_logs = """
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            acao TEXT,
            data TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        self.cursor.execute(sql_create_users)
        self.cursor.execute(sql_create_logs)
        self.conn.commit()

    # --- MÉTODOS DE USO GERAL ---
    
    def adicionar_usuario(self, nome, email):
        try:
            self.cursor.execute("INSERT INTO usuarios (nome, email) VALUES (?, ?)", (nome, email))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False # Email já existe

    def listar_usuarios(self):
        self.cursor.execute("SELECT * FROM usuarios")
        return self.cursor.fetchall()

    def fechar(self):
        if self.conn:
            self.conn.close()