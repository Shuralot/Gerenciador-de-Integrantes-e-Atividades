import sys
import os
import uuid
import firebase_admin
from firebase_admin import credentials, db
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit,
    QPushButton, QVBoxLayout, QTextEdit, QComboBox,
    QListWidget, QListWidgetItem
)
from PyQt6.QtCore import Qt

# Função que resolve o caminho para arquivos externos
def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

# Inicializa o Firebase usando o caminho certo
cred_path = resource_path('metagi-da5b0-firebase-adminsdk-fbsvc-aec7fdba72.json')
cred = credentials.Certificate(cred_path)
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://metagi-da5b0-default-rtdb.firebaseio.com/'
})

root = db.reference('/')

class FirebaseApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gerenciador de Integrantes e Atividades")
        self.setGeometry(100, 100, 500, 600)
        self.setWindowIcon(QIcon('assets/logo.png'))

        # Campos de entrada para Atividades
        self.atividade_input = QLineEdit(self)
        self.atividade_input.setPlaceholderText("Nome da Atividade")

        self.selecionar_integrantes = QListWidget()
        self.selecionar_integrantes.setSelectionMode(QListWidget.SelectionMode.MultiSelection)

        integrantes_list = root.child('integrantes').get()
        if integrantes_list:
            for integrante in integrantes_list.values():
                item = QListWidgetItem(f"{integrante['nome']} - {integrante['funcao']}")
                item.setData(Qt.ItemDataRole.UserRole, integrante)
                self.selecionar_integrantes.addItem(item)

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
            responsaveis = []
            for item in selecionados:
                dados = item.data(Qt.ItemDataRole.UserRole)
                responsaveis.append(dados)

            nova_atividade = {
                'atividade': atividade,
                'status': status,
                'responsaveis': responsaveis
            }

            root.child('atividades').child(str(uuid.uuid4())).set(nova_atividade)
            self.text_area.append(f"✅ Atividade '{atividade}' adicionada!")
            self.atividade_input.clear()
            self.selecionar_integrantes.clearSelection()
            self.status_input.setCurrentIndex(0)
        else:
            self.text_area.append("⚠️ Preencha todos os campos de atividade!")

    def listar_integrantes(self):
        self.text_area.clear()
        integrantes = root.child('integrantes').get()

        self.text_area.append("=== Integrantes ===")
        if integrantes:
            documentistas = []
            desenvolvedores = []
            gerentes = []

            for id, dados in integrantes.items():
                funcao = dados.get('funcao', '')
                if funcao == 'Documentista':
                    documentistas.append(dados['nome'])
                elif funcao == 'Desenvolvedor':
                    desenvolvedores.append(dados['nome'])
                elif funcao == 'Gerente':
                    gerentes.append(dados['nome'])

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
        atividades = root.child('atividades').get()

        self.text_area.append("\n=== Atividades ===")
        if atividades:
            todo = []
            doing = []
            done = []

            for id, dados in atividades.items():
                status = dados.get('status', '').lower()
                atividade = dados.get('atividade', 'Sem nome')
                responsaveis = dados.get('responsaveis', [])

                texto_responsaveis = ', '.join(
                    [f"{r.get('nome')} ({r.get('funcao')})" for r in responsaveis]
                )

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
    janela = FirebaseApp()
    janela.show()
    sys.exit(app.exec())
