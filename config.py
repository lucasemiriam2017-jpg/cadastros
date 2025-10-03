import os

class Config:
    # URL do banco, pode vir do Render ou do .env local
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "postgresql://usuario:senha@localhost:5432/meubanco")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = "uploads"
