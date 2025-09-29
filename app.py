from flask import Flask, render_template, request, redirect, send_file
import smtplib
from email.message import EmailMessage
import os
import csv

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
CSV_FILE = "cadastros.csv"

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Cria o CSV se não existir
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Nome", "CPF", "Instituição", "E-mail", "Telefone", "Arquivo"])

EMAIL_ORIGEM = "seuemail@gmail.com"       # seu e-mail
EMAIL_DESTINO = "destinatario@email.com"  # e-mail que vai receber os cadastros
SENHA_APP = "SUA_SENHA_DE_APP"            # senha de app do Gmail

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

    # Salvar arquivo enviado
    arquivo = request.files.get("arquivo")
    arquivo_nome = ""
    if arquivo:
        arquivo_nome = arquivo.filename
        caminho = os.path.join(UPLOAD_FOLDER, arquivo_nome)
        arquivo.save(caminho)

    # Salvar no CSV
    with open(CSV_FILE, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow([nome, cpf, instituicao, email_usuario, telefone, arquivo_nome])

    # Enviar e-mail
    msg = EmailMessage()
    msg["Subject"] = "Novo cadastro de cliente"
    msg["From"] = EMAIL_ORIGEM
    msg["To"] = EMAIL_DESTINO

    corpo = f"""
Novo cadastro recebido:

Nome: {nome}
CPF: {cpf}
Instituição: {instituicao}
E-mail do usuário: {email_usuario}
Telefone: {telefone}
Arquivo: {arquivo_nome}
"""
    msg.set_content(corpo)

    if arquivo:
        with open(caminho, "rb") as f:
            conteudo = f.read()
        msg.add_attachment(conteudo, maintype="application", subtype="octet-stream", filename=arquivo_nome)
        os.remove(caminho)  # opcional: apagar após envio

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(EMAIL_ORIGEM, SENHA_APP)
        smtp.send_message(msg)

    return "✅ Cadastro enviado com sucesso!"

# Nova rota para baixar o CSV
@app.route("/baixar-csv")
def baixar_csv():
    return send_file(CSV_FILE, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)





