from flask import Flask, render_template, request, redirect, url_for, session, send_file
import os
import csv
from datetime import datetime
import pandas as pd
from io import BytesIO
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

app = Flask(__name__)
app.secret_key = "chave-secreta-muito-segura"

UPLOAD_FOLDER = "uploads"
CSV_FILE = "cadastros.csv"

# Credenciais do admin
ADMIN_USER = "convenios2025"
ADMIN_PASS = "conv@2025*"

# Google Sheets config
SERVICE_ACCOUNT_FILE = 'service_account.json'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SPREADSHEET_ID = 'SEU_SPREADSHEET_ID'
RANGE_NAME = 'Sheet1!A1:G1000'

# Cria pastas e CSV se não existirem
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Data", "Nome", "CPF", "Instituição", "E-mail", "Telefone", "Arquivo"])

# ---------- Funções Google Sheets ----------
def get_sheet_service():
    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('sheets', 'v4', credentials=creds)
    return service.spreadsheets()

def send_to_sheets(data):
    try:
        sheet = get_sheet_service()
        values = [[data["Data"], data["Nome"], data["CPF"], data["Instituição"],
                   data["E-mail"], data["Telefone"], data["Arquivo"]]]
        body = {"values": values}
        sheet.values().append(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME,
                              valueInputOption="USER_ENTERED", body=body).execute()
        return True
    except Exception as e:
        print("Erro Google Sheets:", e)
        return False

# ---------- ROTAS PÚBLICAS ----------
@app.route("/")
def index():
    return render_template("form.html")

@app.route("/enviar", methods=["POST"])
def enviar():
    nome = request.form["nome"]
    cpf = request.form["cpf"]
    instituicao = request.form["instituicao"]
    email_usuario = request.form["email_usuario"]
    telefone = request.form["telefone"]

    arquivo = request.files.get("arquivo")
    nome_arquivo = ""
    if arquivo and arquivo.filename != "":
        nome_arquivo = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{arquivo.filename}"
        arquivo.save(os.path.join(UPLOAD_FOLDER, nome_arquivo))

    data = {
        "Data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Nome": nome,
        "CPF": cpf,
        "Instituição": instituicao,
        "E-mail": email_usuario,
        "Telefone": telefone,
        "Arquivo": nome_arquivo
    }

    # Salva no CSV local
    with open(CSV_FILE, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(data.values())

    # Envia para Google Sheets
    send_to_sheets(data)

    return "✅ Cadastro enviado com sucesso!"

# ---------- ROTAS ADMIN ----------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form.get("usuario") == ADMIN_USER and request.form.get("senha") == ADMIN_PASS:
            session["logged_in"] = True
            return redirect(url_for("lista"))
        else:
            return render_template("login.html", error="❌ Usuário ou senha inválidos")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("logged_in", None)
    return render_template("logout.html")

@app.route("/lista")
def lista():
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    cadastros = []
    with open(CSV_FILE, mode='r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            cadastros.append(row)
    return render_template("lista.html", cadastros=cadastros, error=None)

@app.route("/baixar-csv")
def baixar_csv():
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    cadastros = []
    with open(CSV_FILE, mode='r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            cadastros.append(row)
    df = pd.DataFrame(cadastros)
    output = BytesIO()
    df.to_csv(output, index=False)
    output.seek(0)
    return send_file(output, as_attachment=True, download_name="cadastros.csv", mimetype="text/csv")

@app.route("/ver-uploads")
def ver_uploads():
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    arquivos = os.listdir(UPLOAD_FOLDER)
    arquivos = [f for f in arquivos if os.path.isfile(os.path.join(UPLOAD_FOLDER, f))]
    return render_template("uploads.html", arquivos=arquivos)

@app.route("/uploads/<filename>")
def uploads(filename):
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    return send_file(os.path.join(UPLOAD_FOLDER, filename))

# ---------- MAIN ----------
if __name__ == "__main__":
    app.run(debug=True)

























