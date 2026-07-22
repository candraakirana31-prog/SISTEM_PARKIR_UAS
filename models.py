from datetime import datetime
from extensions import db
from werkzeug.security import generate_password_hash, check_password_hash


class Admin(db.Model):
    """Akun petugas / admin Sistem Manajemen Parkir Kampus."""

    __tablename__ = "admin"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    nama_lengkap = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


JENIS_KENDARAAN = ["Motor", "Mobil"]
JENIS_PENGGUNA = ["Mahasiswa", "Dosen", "Staff", "Tamu"]


class AreaParkir(db.Model):
    """Zona / area parkir di lingkungan kampus (mis. Gedung A, Parkir Timur)."""

    __tablename__ = "area_parkir"

    id = db.Column(db.Integer, primary_key=True)
    nama_area = db.Column(db.String(100), unique=True, nullable=False)
    lokasi = db.Column(db.String(150), nullable=True)
    kapasitas = db.Column(db.Integer, nullable=False, default=0)
    keterangan = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    transaksi = db.relationship(
        "Transaksi", backref="area", cascade="all, delete-orphan", lazy=True
    )

    @property
    def terpakai(self):
        return sum(1 for t in self.transaksi if t.status == "Masih Parkir")

    @property
    def tersedia(self):
        return max(self.kapasitas - self.terpakai, 0)

    @property
    def penuh(self):
        return self.terpakai >= self.kapasitas


class Kendaraan(db.Model):
    """Data kendaraan yang terdaftar di sistem parkir kampus."""

    __tablename__ = "kendaraan"

    id = db.Column(db.Integer, primary_key=True)
    plat_nomor = db.Column(db.String(20), unique=True, nullable=False)
    jenis_kendaraan = db.Column(db.String(10), nullable=False)  # Motor / Mobil
    nama_pemilik = db.Column(db.String(100), nullable=False)
    nim_nip = db.Column(db.String(30), nullable=True)
    jenis_pengguna = db.Column(db.String(20), nullable=False)  # Mahasiswa/Dosen/Staff/Tamu
    kontak = db.Column(db.String(30), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    transaksi = db.relationship(
        "Transaksi", backref="kendaraan", cascade="all, delete-orphan", lazy=True
    )

    @property
    def sedang_parkir(self):
        return any(t.status == "Masih Parkir" for t in self.transaksi)

    @property
    def total_kunjungan(self):
        return len(self.transaksi)


STATUS_TRANSAKSI = ["Masih Parkir", "Sudah Keluar"]


class Transaksi(db.Model):
    """Catatan keluar-masuk kendaraan (menghubungkan Kendaraan & AreaParkir)."""

    __tablename__ = "transaksi"

    id = db.Column(db.Integer, primary_key=True)
    kendaraan_id = db.Column(db.Integer, db.ForeignKey("kendaraan.id"), nullable=False)
    area_id = db.Column(db.Integer, db.ForeignKey("area_parkir.id"), nullable=False)

    waktu_masuk = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    waktu_keluar = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(20), nullable=False, default=STATUS_TRANSAKSI[0])
    petugas = db.Column(db.String(100), nullable=False)
    catatan = db.Column(db.String(255), nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def durasi_menit(self):
        akhir = self.waktu_keluar or datetime.utcnow()
        selisih = akhir - self.waktu_masuk
        return int(selisih.total_seconds() // 60)

    @property
    def durasi_display(self):
        menit = self.durasi_menit
        jam, sisa = divmod(menit, 60)
        if jam:
            return f"{jam} jam {sisa} menit"
        return f"{sisa} menit"
