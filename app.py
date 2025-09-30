from flask import Flask, render_template, request, send_file
import os
import csv
from datetime import datetime

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
CSV_FILE = "cadastros.csv"

# Cria pastas e CSV se não existirem
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Data", "Nome", "CPF", "Instituição", "E-mail", "Telefone", "Arquivo"])

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

    # Salvar arquivo, se houver
    arquivo = request.files.get("arquivo")
    nome_arquivo = ""
    if arquivo and arquivo.filename != "":
        nome_arquivo = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{arquivo.filename}"
        caminho = os.path.join(UPLOAD_FOLDER, nome_arquivo)
        arquivo.save(caminho)

    # Salvar dados no CSV
    with open(CSV_FILE, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            nome, cpf, instituicao, email_usuario, telefone, nome_arquivo
        ])

    return "✅ Cadastro enviado com sucesso!"

# Nova rota para baixar o CSV
@app.route("/baixar-csv")
def baixar_csv():
    return send_file(CSV_FILE, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)







