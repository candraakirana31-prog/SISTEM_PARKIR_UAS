import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    # Ganti SECRET_KEY ini dengan string acak yang aman saat deploy ke production
    SECRET_KEY = os.environ.get("SECRET_KEY", "ganti-dengan-secret-key-yang-aman")

    DATABASE_URL = os.environ.get(
        "DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, 'parkir_kampus.db')}"
    )
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    NAMA_KAMPUS = os.environ.get("NAMA_KAMPUS", "Universitas Bale Bandung")