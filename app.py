from flask import Flask, render_template, request, send_file, redirect, url_for, session
import os
from datetime import datetime
from io import BytesIO
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor

# -------------------- CONFIGURAÇÃO --------------------
load_dotenv()
app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret")  # fallback dev

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Credenciais do admin
ADMIN_USER = os.environ.get("ADMIN_USER")
ADMIN_PASS = os.environ.get("ADMIN_PASS")

# -------------------- CONEXÃO COM POSTGRES --------------------
DATABASE_URL = os.environ.get("DATABASE_URL")  # URL do Neon no Render
conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
cursor = conn.cursor()

# Cria tabela se não existir
cursor.execute("""
CREATE TABLE IF NOT EXISTS cadastros (
    id SERIAL PRIMARY KEY,
    data TIMESTAMP DEFAULT NOW(),
    nome TEXT,
    cpf TEXT,
    instituicao TEXT,
    email_usuario TEXT,
    telefone TEXT,
    nome_arquivo TEXT,
    arquivo_bytes BYTEA,
    lgpd_aceite TEXT
)
""")
conn.commit()

# -------------------- FUNÇÕES AUXILIARES --------------------
def salvar_cadastro(nome, cpf, instituicao, email_usuario, telefone, nome_arquivo, arquivo_bytes, lgpd_aceite):
    cursor.execute("""
        INSERT INTO cadastros (nome, cpf, instituicao, email_usuario, telefone, nome_arquivo, arquivo_bytes, lgpd_aceite)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, (nome, cpf, instituicao, email_usuario, telefone, nome_arquivo, arquivo_bytes, lgpd_aceite))
    conn.commit()

def listar_cadastros():
    cursor.execute("SELECT * FROM cadastros ORDER BY id DESC")
    return cursor.fetchall()

def obter_arquivo(cadastro_id):
    cursor.execute("SELECT nome_arquivo, arquivo_bytes FROM cadastros WHERE id = %s", (cadastro_id,))
    return cursor.fetchone()

# -------------------- ROTAS PÚBLICAS --------------------
@app.route("/")
def index():
    """Página inicial com formulário de cadastro"""
    return render_template("form.html")

@app.route("/enviar", methods=["POST"])
def enviar():
    """Recebe dados do formulário e salva no banco + upload de arquivo"""
    nome = request.form.get("nome", "")
    cpf = request.form.get("cpf", "")
    instituicao = request.form.get("instituicao", "")
    email_usuario = request.form.get("email_usuario", "")
    telefone = request.form.get("telefone", "")
    lgpd_aceite = request.form.get("lgpd_aceite", "Não informado")

    # Salvar arquivo, se houver
    arquivo = request.files.get("arquivo")
    nome_arquivo = None
    arquivo_bytes = None
    if arquivo and arquivo.filename != "":
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        nome_arquivo = f"{timestamp}_{arquivo.filename}"
        arquivo_bytes = arquivo.read()

    # Salvar dados no PostgreSQL
    salvar_cadastro(nome, cpf, instituicao, email_usuario, telefone, nome_arquivo, arquivo_bytes, lgpd_aceite)

    return render_template("obrigado.html", nome=nome, instituicao=instituicao)

# -------------------- ROTAS ADMIN --------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    """Login do administrador"""
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
    """Logout do administrador"""
    session.pop("logged_in", None)
    return render_template("logout.html")

@app.route("/lista")
def lista():
    """Exibe todos os cadastros para o admin"""
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    cadastros = listar_cadastros()
    return render_template("lista.html", cadastros=cadastros)

@app.route("/baixar-csv")
def baixar_csv():
    """Permite baixar o CSV de cadastros"""
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    
    import csv
    from io import StringIO
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["Data", "Nome", "CPF", "Instituição", "E-mail", "Telefone", "Arquivo", "LGPD"])
    for c in listar_cadastros():
        writer.writerow([c['data'], c['nome'], c['cpf'], c['instituicao'], c['email_usuario'], c['telefone'], c['nome_arquivo'], c['lgpd_aceite']])
    output.seek(0)
    
    from flask import Response
    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=cadastros.csv"}
    )

@app.route("/uploads/<int:cadastro_id>")
def uploads(cadastro_id):
    """Baixar ou visualizar arquivo específico"""
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    arquivo = obter_arquivo(cadastro_id)
    if not arquivo or not arquivo['arquivo_bytes']:
        return "Arquivo não encontrado", 404
    return send_file(BytesIO(arquivo['arquivo_bytes']), download_name=arquivo['nome_arquivo'], as_attachment=True)

# -------------------- MAIN --------------------
if __name__ == "__main__":
    app.run(debug=True)




