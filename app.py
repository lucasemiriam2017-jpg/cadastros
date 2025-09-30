from flask import Flask, render_template, request, send_file, redirect, url_for, session
import os
import csv
from datetime import datetime

app = Flask(__name__)
app.secret_key = "chave-secreta-muito-segura"  # troque por algo mais forte

UPLOAD_FOLDER = "uploads"
CSV_FILE = "cadastros.csv"

# Credenciais do admin
ADMIN_USER = "admin"
ADMIN_PASS = "1234"

# Cria pastas e CSV se não existirem
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Data", "Nome", "CPF", "Instituição", "E-mail", "Telefone", "Arquivo"])

# -------------------- ROTAS PÚBLICAS --------------------

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
        writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                         nome, cpf, instituicao, email_usuario, telefone, nome_arquivo])

    return "✅ Cadastro enviado com sucesso!"

# -------------------- ROTAS ADMIN --------------------

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = request.form.get("usuario")
        senha = request.form.get("senha")
        if usuario == ADMIN_USER and senha == ADMIN_PASS:
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
    error = None
    try:
        with open(CSV_FILE, mode='r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                cadastros.append(row)
    except Exception as e:
        error = str(e)
    return render_template("lista.html", cadastros=cadastros, error=error)

@app.route("/baixar-csv")
def baixar_csv():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    return send_file(CSV_FILE, as_attachment=True)

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

# -------------------- MAIN --------------------

if __name__ == "__main__":
    app.run(debug=True)






















