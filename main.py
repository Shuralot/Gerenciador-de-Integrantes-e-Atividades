import sys
import os
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit,
    QPushButton, QVBoxLayout, QTextEdit, QComboBox,
    QListWidget, QListWidgetItem
)
from PyQt6.QtCore import Qt

from database import DatabaseManager

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath('.'), relative_path)

# Inicializa DB
db_manager = DatabaseManager()

# Seed inicial se não houver integrantes
if not db_manager.listar_integrantes():
    db_manager.add_integrante("Fulano", "Desenvolvedor")
    db_manager.add_integrante("Beltrano", "Documentista")
    db_manager.add_integrante("Ciclano", "Gerente")

class MainApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gerenciador de Integrantes e Atividades")
        self.setGeometry(100, 100, 500, 600)
        self.setWindowIcon(QIcon(resource_path('assets/logo.png')))

        self.db = db_manager

        # Campos de entrada para Atividades
        self.atividade_input = QLineEdit(self)
        self.atividade_input.setPlaceholderText("Nome da Atividade")

        # Campos para gerenciar integrantes
        self.nome_integrante_input = QLineEdit(self)
        self.nome_integrante_input.setPlaceholderText("Nome do integrante")
        self.funcao_input = QLineEdit(self)
        self.funcao_input.setPlaceholderText("Função (ex: Desenvolvedor)")

        self.add_integrante_btn = QPushButton("Adicionar Integrante")
        self.add_integrante_btn.clicked.connect(self.adicionar_integrante)

        self.remove_integrante_btn = QPushButton("Remover Integrante Selecionado")
        self.remove_integrante_btn.clicked.connect(self.remover_integrante)

        self.selecionar_integrantes = QListWidget()
        self.selecionar_integrantes.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        # popula a lista
        self.refresh_integrantes()

        self.status_input = QComboBox()
        self.status_input.addItem('A Fazer', 'todo')
        self.status_input.addItem('Fazendo', 'doing')
        self.status_input.addItem('Concluído', 'done')

        self.add_atividade_btn = QPushButton("Adicionar Atividade")
        self.add_atividade_btn.clicked.connect(self.adicionar_atividade)

        self.listar_atividades_btn = QPushButton("Listar Atividades")
        self.listar_atividades_btn.clicked.connect(self.listar_atividades)

        self.listar_integrantes_btn = QPushButton("Listar Integrantes")
        self.listar_integrantes_btn.clicked.connect(self.listar_integrantes)

        # Área de exibição
        self.text_area = QTextEdit()
        self.text_area.setReadOnly(True)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Atividades:"))
        layout.addWidget(self.atividade_input)
        layout.addWidget(QLabel("Gerenciar Integrantes:"))
        layout.addWidget(self.nome_integrante_input)
        layout.addWidget(self.funcao_input)
        layout.addWidget(self.add_integrante_btn)
        layout.addWidget(self.remove_integrante_btn)
        layout.addWidget(QLabel("Integrantes na atividade:"))
        layout.addWidget(self.selecionar_integrantes)
        layout.addWidget(QLabel("Status da atividade:"))
        layout.addWidget(self.status_input)
        layout.addWidget(self.add_atividade_btn)
        layout.addWidget(self.listar_integrantes_btn)
        layout.addWidget(self.listar_atividades_btn)
        layout.addWidget(QLabel("Resultado:"))
        layout.addWidget(self.text_area)

        self.setLayout(layout)

    def adicionar_atividade(self):
        atividade = self.atividade_input.text()
        status = self.status_input.currentData()
        selecionados = self.selecionar_integrantes.selectedItems()
        if atividade and status and selecionados:
            responsaveis_ids = []
            for item in selecionados:
                dados = item.data(Qt.ItemDataRole.UserRole)
                # dados deve conter 'id'
                responsaveis_ids.append(dados.get('id'))

            sucesso = self.db.add_atividade(atividade, status, responsaveis_ids)
            if sucesso:
                self.text_area.append(f"✅ Atividade '{atividade}' adicionada!")
                self.atividade_input.clear()
                self.selecionar_integrantes.clearSelection()
                self.status_input.setCurrentIndex(0)
            else:
                self.text_area.append("❌ Erro ao salvar atividade no banco.")
        else:
            self.text_area.append("⚠️ Preencha todos os campos de atividade!")

    def refresh_integrantes(self):
        self.selecionar_integrantes.clear()
        integrantes_list = self.db.listar_integrantes()
        if integrantes_list:
            for integrante in integrantes_list:
                item = QListWidgetItem(f"{integrante['nome']} - {integrante.get('funcao','')}")
                item.setData(Qt.ItemDataRole.UserRole, integrante)
                self.selecionar_integrantes.addItem(item)

    def adicionar_integrante(self):
        nome = self.nome_integrante_input.text().strip()
        funcao = self.funcao_input.text().strip()
        if not nome:
            self.text_area.append("⚠️ Informe o nome do integrante.")
            return

        rid = self.db.add_integrante(nome, funcao or None)
        if rid:
            self.text_area.append(f"✅ Integrante '{nome}' adicionado.")
            self.nome_integrante_input.clear()
            self.funcao_input.clear()
            self.refresh_integrantes()
        else:
            self.text_area.append("❌ Erro ao adicionar integrante.")

    def remover_integrante(self):
        selecionados = self.selecionar_integrantes.selectedItems()
        if not selecionados:
            self.text_area.append("⚠️ Selecione um integrante para remover.")
            return

        for item in selecionados:
            dados = item.data(Qt.ItemDataRole.UserRole)
            integrante_id = dados.get('id')
            if integrante_id:
                sucesso = self.db.delete_integrante(integrante_id)
                if sucesso:
                    self.text_area.append(f"🗑️ Integrante '{dados.get('nome')}' removido.")
                else:
                    self.text_area.append(f"❌ Erro ao remover '{dados.get('nome')}'.")

        self.refresh_integrantes()

    def listar_integrantes(self):
        self.text_area.clear()
        integrantes = self.db.listar_integrantes()

        self.text_area.append("=== Integrantes ===")
        if integrantes:
            documentistas = []
            desenvolvedores = []
            gerentes = []

            for dados in integrantes:
                funcao = dados.get('funcao', '')
                nome = dados.get('nome')
                if funcao == 'Documentista':
                    documentistas.append(nome)
                elif funcao == 'Desenvolvedor':
                    desenvolvedores.append(nome)
                elif funcao == 'Gerente':
                    gerentes.append(nome)

            self.text_area.append("\nDocumentistas:")
            for nome in documentistas:
                self.text_area.append(f"- {nome}")

            self.text_area.append("\nDesenvolvedores:")
            for nome in desenvolvedores:
                self.text_area.append(f"- {nome}")

            self.text_area.append("\nGerentes:")
            for nome in gerentes:
                self.text_area.append(f"- {nome}")
        else:
            self.text_area.append("Nenhum integrante cadastrado.")

    def listar_atividades(self):
        self.text_area.clear()
        atividades = self.db.get_atividades()

        self.text_area.append("\n=== Atividades ===")
        if atividades:
            todo = []
            doing = []
            done = []

            for dados in atividades:
                status = (dados.get('status') or '').lower()
                atividade = dados.get('atividade', 'Sem nome')
                responsaveis = dados.get('responsaveis', [])

                texto_responsaveis = ', '.join(
                    [f"{r.get('nome')} ({r.get('funcao')})" for r in responsaveis]
                ) if responsaveis else 'Sem responsáveis'

                linha = f"- {atividade} \n Responsáveis: {texto_responsaveis}"

                if status == 'todo':
                    todo.append(linha)
                elif status == 'doing':
                    doing.append(linha)
                elif status == 'done':
                    done.append(linha)

            self.text_area.append("\n-- To Do --")
            self.text_area.append('\n'.join(todo) if todo else "Nenhuma atividade em To Do.")

            self.text_area.append("\n-- Doing --")
            self.text_area.append('\n'.join(doing) if doing else "Nenhuma atividade em Doing.")

            self.text_area.append("\n-- Done --")
            self.text_area.append('\n'.join(done) if done else "Nenhuma atividade em Done.")
        else:
            self.text_area.append("Nenhuma atividade cadastrada.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    janela = MainApp()
    janela.show()
    sys.exit(app.exec())
