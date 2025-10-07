import os

# Caminhos padrão
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
CSV_FILE = os.path.join(BASE_DIR, "cadastros.csv")

# Cria as pastas se não existirem
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

