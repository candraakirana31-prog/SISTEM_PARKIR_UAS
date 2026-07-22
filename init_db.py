"""
Jalankan sekali aja setelah DATABASE_URL production sudah di-set,
untuk membuat semua tabel di database Postgres.
"""
from app import app
from extensions import db

with app.app_context():
    db.create_all()
    print("Tabel berhasil dibuat.")