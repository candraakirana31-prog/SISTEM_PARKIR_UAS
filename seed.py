"""
Jalankan sekali untuk mengisi data awal:
    python seed.py
Membuat 1 akun admin default dan beberapa contoh data
(aman dijalankan berkali-kali; tidak akan membuat duplikat).
"""

from datetime import datetime, timedelta

from app import create_app
from extensions import db
from models import Admin, AreaParkir, Kendaraan, Transaksi

app = create_app()

with app.app_context():
    # --- Akun admin default ---
    admin = Admin.query.filter_by(username="CandraKIrana").first()
    if not admin:
        admin = Admin.query.filter_by(username="admin").first()

    if not admin:
        admin = Admin(nama_lengkap="Admin Parkir Kampus")
        db.session.add(admin)

    admin.username = "CandraKIrana"
    admin.set_password("CandraKirana31")
    print("Akun admin disiapkan -> username: CandraKIrana | password: CandraKirana31")

    db.session.commit()

    # --- Contoh area parkir ---
    area_data = [
        {"nama_area": "Gedung Rektorat", "lokasi": "Depan Gedung Rektorat", "kapasitas": 30},
        {"nama_area": "Parkir Fakultas Teknik", "lokasi": "Sisi Timur Gedung Teknik", "kapasitas": 20},
        {"nama_area": "Parkir Perpustakaan", "lokasi": "Belakang Perpustakaan Pusat", "kapasitas": 15},
    ]
    area_map = {}
    for a in area_data:
        area = AreaParkir.query.filter_by(nama_area=a["nama_area"]).first()
        if not area:
            area = AreaParkir(**a)
            db.session.add(area)
            db.session.flush()
        area_map[a["nama_area"]] = area
    db.session.commit()

    # --- Contoh kendaraan ---
    kendaraan_data = [
        {"plat_nomor": "B 1234 ABC", "jenis_kendaraan": "Motor", "nama_pemilik": "Budi Santoso",
         "nim_nip": "21106001", "jenis_pengguna": "Mahasiswa", "kontak": "081234567890"},
        {"plat_nomor": "B 5678 XYZ", "jenis_kendaraan": "Mobil", "nama_pemilik": "Dr. Siti Aminah",
         "nim_nip": "198501012010", "jenis_pengguna": "Dosen", "kontak": "081298765432"},
        {"plat_nomor": "D 4321 DEF", "jenis_kendaraan": "Motor", "nama_pemilik": "Rina Wijaya",
         "nim_nip": "22106045", "jenis_pengguna": "Mahasiswa", "kontak": "085712345678"},
    ]
    kendaraan_map = {}
    for k in kendaraan_data:
        kendaraan = Kendaraan.query.filter_by(plat_nomor=k["plat_nomor"]).first()
        if not kendaraan:
            kendaraan = Kendaraan(**k)
            db.session.add(kendaraan)
            db.session.flush()
        kendaraan_map[k["plat_nomor"]] = kendaraan
    db.session.commit()

    # --- Contoh transaksi (1 masih parkir, 1 sudah keluar) ---
    if Transaksi.query.count() == 0:
        db.session.add(Transaksi(
            kendaraan_id=kendaraan_map["B 1234 ABC"].id,
            area_id=area_map["Gedung Rektorat"].id,
            waktu_masuk=datetime.utcnow() - timedelta(hours=2),
            status="Masih Parkir",
            petugas="Petugas Pos 1",
        ))
        db.session.add(Transaksi(
            kendaraan_id=kendaraan_map["B 5678 XYZ"].id,
            area_id=area_map["Parkir Fakultas Teknik"].id,
            waktu_masuk=datetime.utcnow() - timedelta(days=1, hours=3),
            waktu_keluar=datetime.utcnow() - timedelta(days=1, hours=1),
            status="Sudah Keluar",
            petugas="Petugas Pos 2",
        ))
        db.session.commit()
        print("Contoh data area, kendaraan, dan transaksi berhasil dibuat.")
    else:
        print("Data transaksi sudah ada, dilewati.")

    print("Seeding selesai.")
