from flask import Flask, render_template, request, redirect
import smtplib
from email.message import EmailMessage
import os

app = Flask(__name__)

from flask import send_from_directory

@app.route("/teste-logo")
def teste_logo():
    return send_from_directory("static", "logo.png")


UPLOAD_FOLDER = "uploads"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

EMAIL_ORIGEM = "lucasemiriam2017@gmail.com"       # seu e-mail
EMAIL_DESTINO = "lucas.vargas3@farmaciassaojoao.com.br"  # e-mail que vai receber os cadastros
SENHA_APP = "spvo qdyx pblf mqpf"            # senha de app do Gmail

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

    # Criar a mensagem de e-mail
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
"""
    msg.set_content(corpo)

    # Verificar se enviou arquivo
    arquivo = request.files.get("arquivo")
    if arquivo:
        caminho = os.path.join(UPLOAD_FOLDER, arquivo.filename)
        arquivo.save(caminho)
        with open(caminho, "rb") as f:
            conteudo = f.read()
        msg.add_attachment(conteudo, maintype="application", subtype="octet-stream", filename=arquivo.filename)
        # opcional: apagar após envio
        os.remove(caminho)

    # Enviar e-mail
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(EMAIL_ORIGEM, SENHA_APP)
        smtp.send_message(msg)

    return "✅ Cadastro enviado com sucesso!"

if __name__ == "__main__":
    app.run(debug=True)

