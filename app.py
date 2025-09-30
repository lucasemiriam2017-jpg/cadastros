from flask import Flask, render_template, request, send_file, redirect, url_for, session, Response
import os
import csv
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "uma_chave_secreta_super_segura"  # necessário para sessões

UPLOAD_FOLDER = "uploads"
CSV_FILE = "cadastros.csv"

# Usuário e senha administrativos
ADMIN_USER = "convenios"
ADMIN_PASS = "conv@2025*"

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

    # ✅ Mensagem de confirmação sem link para lista
    return "✅ Cadastro enviado com sucesso!"

# -----------------------------
# Rota para baixar o CSV
# -----------------------------
@app.route("/baixar-csv")
def baixar_csv():
    # Verifica se usuário está logado como admin
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    return send_file(CSV_FILE, as_attachment=True)

# -----------------------------
# Servir arquivos da pasta uploads
# -----------------------------
@app.route("/uploads/<filename>")
def uploads(filename):
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    return send_file(os.path.join(UPLOAD_FOLDER, filename))

# -----------------------------
# Rota para listar arquivos enviados
# -----------------------------
@app.route("/ver-uploads")
def ver_uploads():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    arquivos = os.listdir(UPLOAD_FOLDER)
    arquivos = [f for f in arquivos if os.path.isfile(os.path.join(UPLOAD_FOLDER, f))]
    links = [f"<a href='/uploads/{a}' target='_blank'>{a}</a>" for a in arquivos]
    return "<h2>📁 Arquivos enviados</h2><br>" + "<br>".join(links)

# -----------------------------
# Rota de login admin
# -----------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = request.form.get("usuario")
        senha = request.form.get("senha")
        if usuario == ADMIN_USER and senha == ADMIN_PASS:
            session["logged_in"] = True
            return redirect(url_for("lista"))
        else:
            return "❌ Usuário ou senha incorretos!"
    return """
    <h2>Login Administrativo</h2>
    <form method="post">
        Usuário: <input type="text" name="usuario"><br>
        Senha: <input type="password" name="senha"><br>
        <button type="submit">Entrar</button>
    </form>
    """

# -----------------------------
# Rota de logout
# -----------------------------
@app.route("/logout")
def logout():
    session.clear()
    return "✅ Logout realizado! <a href='/login'>Login novamente</a>"

# -----------------------------
# Rota para listar cadastros
# -----------------------------
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

# -----------------------------
# Inicialização
# -----------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)




















