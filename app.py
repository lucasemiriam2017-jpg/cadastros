from flask import Flask, render_template, request, send_file, redirect, url_for
import os
import csv
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
CSV_FILE = "cadastros.csv"

# Cria pastas se não existirem
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Data", "Nome", "CPF", "Instituição", "E-mail", "Telefone", "Arquivo"])

# -----------------------------
# Rota do formulário
# -----------------------------
@app.route("/")
def index():
    return render_template("form.html")

# -----------------------------
# Rota de envio do cadastro
# -----------------------------
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
        nome_arquivo = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{secure_filename(arquivo.filename)}"
        caminho = os.path.join(UPLOAD_FOLDER, nome_arquivo)
        arquivo.save(caminho)

    # Salvar dados no CSV
    with open(CSV_FILE, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            nome, cpf, instituicao, email_usuario, telefone, nome_arquivo
        ])

    return f"✅ Cadastro enviado com sucesso! <a href='/lista'>Ver lista de cadastros</a>"

# -----------------------------
# Rota para baixar o CSV completo
# -----------------------------
@app.route("/baixar-csv")
def baixar_csv():
    return send_file(CSV_FILE, as_attachment=True)

# -----------------------------
# Rota para listar arquivos enviados
# -----------------------------
@app.route("/ver-uploads")
def ver_uploads():
    arquivos = os.listdir(UPLOAD_FOLDER)
    arquivos = [f for f in arquivos if os.path.isfile(os.path.join(UPLOAD_FOLDER, f))]
    # Criar links clicáveis
    links = [f"<a href='/uploads/{a}' target='_blank'>{a}</a>" for a in arquivos]
    return "<h2>📁 Arquivos enviados</h2><br>" + "<br>".join(links)

# -----------------------------
# Servir arquivos da pasta uploads
# -----------------------------
@app.route("/uploads/<filename>")
def uploads(filename):
    return send_file(os.path.join(UPLOAD_FOLDER, filename))

# -----------------------------
# Rota para listar cadastros (com arquivos clicáveis)
# -----------------------------
@app.route("/lista")
def lista():
    cadastros = []
    error = None
    try:
        with open(CSV_FILE, mode='r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                cadastros.append(row)
    except Exception as e:
        error = str(e)
    return render_template("lista.html", cadastros=cadastros, error=error)

# -----------------------------
# Inicialização
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True)

















