import sys
import os
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit,
    QPushButton, QVBoxLayout, QTextEdit, QComboBox,
    QListWidget, QListWidgetItem, QTabWidget, QHBoxLayout
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

        # --- Construindo abas ---
        self.tabs = QTabWidget()

        # Tab principal (Atividades + gerenciar integrantes)
        main_tab = QWidget()
        main_layout = QVBoxLayout()
        main_layout.addWidget(QLabel("Atividades:"))
        main_layout.addWidget(self.atividade_input)
        main_layout.addWidget(QLabel("Gerenciar Integrantes:"))
        main_layout.addWidget(self.nome_integrante_input)
        main_layout.addWidget(self.funcao_input)
        main_layout.addWidget(self.add_integrante_btn)
        main_layout.addWidget(self.remove_integrante_btn)
        main_layout.addWidget(QLabel("Integrantes na atividade:"))
        main_layout.addWidget(self.selecionar_integrantes)
        main_layout.addWidget(QLabel("Status da atividade:"))
        main_layout.addWidget(self.status_input)
        main_layout.addWidget(self.add_atividade_btn)
        main_layout.addWidget(self.listar_integrantes_btn)
        main_layout.addWidget(self.listar_atividades_btn)
        main_layout.addWidget(QLabel("Resultado:"))
        main_layout.addWidget(self.text_area)
        main_tab.setLayout(main_layout)

        # Tab admin para manipular todos os dados do DB
        admin_tab = QWidget()
        admin_layout = QHBoxLayout()

        # Coluna Integrantes
        col_integrantes = QVBoxLayout()
        col_integrantes.addWidget(QLabel("Integrantes (Admin):"))
        self.admin_integrantes_list = QListWidget()
        col_integrantes.addWidget(self.admin_integrantes_list)
        self.admin_integrantes_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        self.admin_refresh_integrantes_btn = QPushButton("Atualizar Integrantes")
        self.admin_refresh_integrantes_btn.clicked.connect(self.refresh_admin_integrantes)
        self.admin_delete_integrante_btn = QPushButton("Remover Selecionados")
        self.admin_delete_integrante_btn.clicked.connect(self.delete_selected_integrantes_admin)
        col_integrantes.addWidget(self.admin_refresh_integrantes_btn)
        col_integrantes.addWidget(self.admin_delete_integrante_btn)

        # Coluna Atividades
        col_atividades = QVBoxLayout()
        col_atividades.addWidget(QLabel("Atividades (Admin):"))
        self.admin_atividades_list = QListWidget()
        col_atividades.addWidget(self.admin_atividades_list)
        self.admin_atividades_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        self.admin_refresh_atividades_btn = QPushButton("Atualizar Atividades")
        self.admin_refresh_atividades_btn.clicked.connect(self.refresh_admin_atividades)
        self.admin_delete_atividade_btn = QPushButton("Remover Selecionadas")
        self.admin_delete_atividade_btn.clicked.connect(self.delete_selected_atividades_admin)
        col_atividades.addWidget(self.admin_refresh_atividades_btn)
        col_atividades.addWidget(self.admin_delete_atividade_btn)

        admin_layout.addLayout(col_integrantes)
        admin_layout.addLayout(col_atividades)
        admin_tab.setLayout(admin_layout)

        # Adiciona abas
        self.tabs.addTab(main_tab, "Atividades")
        self.tabs.addTab(admin_tab, "Admin")

        # Layout principal da janela
        window_layout = QVBoxLayout()
        window_layout.addWidget(self.tabs)
        self.setLayout(window_layout)

        # popula listas admin
        self.refresh_admin_integrantes()
        self.refresh_admin_atividades()

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

    # --- Admin tab helpers ---
    def refresh_admin_integrantes(self):
        self.admin_integrantes_list.clear()
        integrantes = self.db.listar_integrantes()
        for i in integrantes:
            item = QListWidgetItem(f"[{i.get('id')}] {i.get('nome')} - {i.get('funcao')}")
            item.setData(Qt.ItemDataRole.UserRole, i)
            self.admin_integrantes_list.addItem(item)

    def refresh_admin_atividades(self):
        self.admin_atividades_list.clear()
        atividades = self.db.get_atividades()
        for a in atividades:
            texto = f"[{a.get('id')}] {a.get('atividade')} ({a.get('status')})"
            item = QListWidgetItem(texto)
            item.setData(Qt.ItemDataRole.UserRole, a)
            self.admin_atividades_list.addItem(item)

    def delete_selected_integrantes_admin(self):
        selecionados = self.admin_integrantes_list.selectedItems()
        if not selecionados:
            self.text_area.append("⚠️ Selecione integrantes para remover (Admin).")
            return
        for item in selecionados:
            dados = item.data(Qt.ItemDataRole.UserRole)
            iid = dados.get('id')
            if iid:
                ok = self.db.delete_integrante(iid)
                if ok:
                    self.text_area.append(f"🗑️ Integrante '{dados.get('nome')}' removido (Admin).")
                else:
                    self.text_area.append(f"❌ Erro ao remover '{dados.get('nome')}' (Admin).")
        self.refresh_admin_integrantes()
        self.refresh_integrantes()

    def delete_selected_atividades_admin(self):
        selecionados = self.admin_atividades_list.selectedItems()
        if not selecionados:
            self.text_area.append("⚠️ Selecione atividades para remover (Admin).")
            return
        for item in selecionados:
            dados = item.data(Qt.ItemDataRole.UserRole)
            aid = dados.get('id')
            if aid:
                ok = self.db.delete_atividade(aid)
                if ok:
                    self.text_area.append(f"🗑️ Atividade '{dados.get('atividade')}' removida (Admin).")
                else:
                    self.text_area.append(f"❌ Erro ao remover atividade id={aid} (Admin).")
        self.refresh_admin_atividades()

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
