import firebase_admin
from firebase_admin import credentials, db

# Caminho para o arquivo JSON da chave privada
cred = credentials.Certificate('metagi-da5b0-firebase-adminsdk-fbsvc-aec7fdba72.json')

# Inicializa o Firebase
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://metagi-da5b0-default-rtdb.firebaseio.com/'  # URL do seu Realtime Database
})

ref = db.reference('/')
ref.set({'message': 'Hello, Firebase!'})

print(ref.get())