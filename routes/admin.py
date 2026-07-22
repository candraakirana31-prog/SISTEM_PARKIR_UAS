from functools import wraps
from datetime import datetime, timedelta

from flask import (
    Blueprint, render_template, request, redirect, url_for, session, flash
)

from extensions import db
from models import (
    Kendaraan, AreaParkir, Transaksi,
    JENIS_KENDARAAN, JENIS_PENGGUNA, STATUS_TRANSAKSI,
)

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


def login_required(view_func):
    @wraps(view_func)
    def wrapped(*args, **kwargs):
        if not session.get("admin_id"):
            flash("Silakan login terlebih dahulu.", "danger")
            return redirect(url_for("auth.login"))
        return view_func(*args, **kwargs)
    return wrapped


# ---------- DASHBOARD ----------

@admin_bp.route("/dashboard")
@login_required
def dashboard():
    total_kendaraan = Kendaraan.query.count()
    total_area = AreaParkir.query.count()
    sedang_parkir = Transaksi.query.filter_by(status="Masih Parkir").count()
    total_transaksi = Transaksi.query.count()

    total_kapasitas = db.session.query(db.func.sum(AreaParkir.kapasitas)).scalar() or 0

    daftar_area = AreaParkir.query.order_by(AreaParkir.nama_area.asc()).all()

    # Rekap kunjungan 7 hari terakhir (dari data transaksi, bukan statis)
    tujuh_hari_lalu = datetime.utcnow() - timedelta(days=6)
    transaksi_7hari = (
        Transaksi.query.filter(Transaksi.waktu_masuk >= tujuh_hari_lalu.replace(
            hour=0, minute=0, second=0, microsecond=0
        )).all()
    )
    rekap_harian = {}
    for i in range(7):
        tanggal = (tujuh_hari_lalu + timedelta(days=i)).date()
        rekap_harian[tanggal] = 0
    for t in transaksi_7hari:
        tgl = t.waktu_masuk.date()
        if tgl in rekap_harian:
            rekap_harian[tgl] += 1

    rekap_labels = [tgl.strftime("%d/%m") for tgl in rekap_harian.keys()]
    rekap_values = list(rekap_harian.values())

    # Rekap per jenis pengguna
    rekap_pengguna = {
        jp: Kendaraan.query.filter_by(jenis_pengguna=jp).count() for jp in JENIS_PENGGUNA
    }

    transaksi_terbaru = (
        Transaksi.query.order_by(Transaksi.waktu_masuk.desc()).limit(8).all()
    )

    return render_template(
        "admin/dashboard.html",
        total_kendaraan=total_kendaraan,
        total_area=total_area,
        sedang_parkir=sedang_parkir,
        total_transaksi=total_transaksi,
        total_kapasitas=total_kapasitas,
        daftar_area=daftar_area,
        rekap_labels=rekap_labels,
        rekap_values=rekap_values,
        rekap_pengguna=rekap_pengguna,
        transaksi_terbaru=transaksi_terbaru,
    )


# ---------- CRUD KENDARAAN ----------

@admin_bp.route("/kendaraan")
@login_required
def kendaraan_list():
    q = request.args.get("q", "").strip()
    query = Kendaraan.query
    if q:
        like = f"%{q}%"
        query = query.filter(
            db.or_(Kendaraan.plat_nomor.ilike(like), Kendaraan.nama_pemilik.ilike(like))
        )
    daftar_kendaraan = query.order_by(Kendaraan.created_at.desc()).all()
    return render_template("admin/kendaraan_list.html", daftar_kendaraan=daftar_kendaraan, q=q)


@admin_bp.route("/kendaraan/tambah", methods=["GET", "POST"])
@login_required
def kendaraan_tambah():
    if request.method == "POST":
        plat_nomor = request.form.get("plat_nomor", "").strip().upper()
        jenis_kendaraan = request.form.get("jenis_kendaraan", "")
        nama_pemilik = request.form.get("nama_pemilik", "").strip()
        nim_nip = request.form.get("nim_nip", "").strip()
        jenis_pengguna = request.form.get("jenis_pengguna", "")
        kontak = request.form.get("kontak", "").strip()

        errors = []
        if not plat_nomor:
            errors.append("Plat nomor wajib diisi.")
        elif Kendaraan.query.filter_by(plat_nomor=plat_nomor).first():
            errors.append("Plat nomor sudah terdaftar.")
        if jenis_kendaraan not in JENIS_KENDARAAN:
            errors.append("Jenis kendaraan tidak valid.")
        if not nama_pemilik:
            errors.append("Nama pemilik wajib diisi.")
        if jenis_pengguna not in JENIS_PENGGUNA:
            errors.append("Jenis pengguna tidak valid.")

        if errors:
            for e in errors:
                flash(e, "danger")
            return render_template(
                "admin/kendaraan_form.html", mode="tambah", kendaraan=None,
                jenis_kendaraan_list=JENIS_KENDARAAN, jenis_pengguna_list=JENIS_PENGGUNA,
            )

        db.session.add(Kendaraan(
            plat_nomor=plat_nomor, jenis_kendaraan=jenis_kendaraan,
            nama_pemilik=nama_pemilik, nim_nip=nim_nip or None,
            jenis_pengguna=jenis_pengguna, kontak=kontak or None,
        ))
        db.session.commit()
        flash("Kendaraan baru berhasil didaftarkan.", "success")
        return redirect(url_for("admin.kendaraan_list"))

    return render_template(
        "admin/kendaraan_form.html", mode="tambah", kendaraan=None,
        jenis_kendaraan_list=JENIS_KENDARAAN, jenis_pengguna_list=JENIS_PENGGUNA,
    )


@admin_bp.route("/kendaraan/<int:kendaraan_id>/edit", methods=["GET", "POST"])
@login_required
def kendaraan_edit(kendaraan_id):
    kendaraan = Kendaraan.query.get_or_404(kendaraan_id)

    if request.method == "POST":
        plat_nomor = request.form.get("plat_nomor", "").strip().upper()
        jenis_kendaraan = request.form.get("jenis_kendaraan", "")
        nama_pemilik = request.form.get("nama_pemilik", "").strip()
        nim_nip = request.form.get("nim_nip", "").strip()
        jenis_pengguna = request.form.get("jenis_pengguna", "")
        kontak = request.form.get("kontak", "").strip()

        errors = []
        if not plat_nomor:
            errors.append("Plat nomor wajib diisi.")
        else:
            duplikat = Kendaraan.query.filter(
                Kendaraan.plat_nomor == plat_nomor, Kendaraan.id != kendaraan_id
            ).first()
            if duplikat:
                errors.append("Plat nomor sudah digunakan kendaraan lain.")
        if jenis_kendaraan not in JENIS_KENDARAAN:
            errors.append("Jenis kendaraan tidak valid.")
        if not nama_pemilik:
            errors.append("Nama pemilik wajib diisi.")
        if jenis_pengguna not in JENIS_PENGGUNA:
            errors.append("Jenis pengguna tidak valid.")

        if errors:
            for e in errors:
                flash(e, "danger")
            return render_template(
                "admin/kendaraan_form.html", mode="edit", kendaraan=kendaraan,
                jenis_kendaraan_list=JENIS_KENDARAAN, jenis_pengguna_list=JENIS_PENGGUNA,
            )

        kendaraan.plat_nomor = plat_nomor
        kendaraan.jenis_kendaraan = jenis_kendaraan
        kendaraan.nama_pemilik = nama_pemilik
        kendaraan.nim_nip = nim_nip or None
        kendaraan.jenis_pengguna = jenis_pengguna
        kendaraan.kontak = kontak or None
        db.session.commit()
        flash("Data kendaraan berhasil diperbarui.", "success")
        return redirect(url_for("admin.kendaraan_list"))

    return render_template(
        "admin/kendaraan_form.html", mode="edit", kendaraan=kendaraan,
        jenis_kendaraan_list=JENIS_KENDARAAN, jenis_pengguna_list=JENIS_PENGGUNA,
    )


@admin_bp.route("/kendaraan/<int:kendaraan_id>/hapus", methods=["POST"])
@login_required
def kendaraan_hapus(kendaraan_id):
    kendaraan = Kendaraan.query.get_or_404(kendaraan_id)
    db.session.delete(kendaraan)
    db.session.commit()
    flash("Data kendaraan berhasil dihapus.", "success")
    return redirect(url_for("admin.kendaraan_list"))


# ---------- CRUD AREA PARKIR ----------

@admin_bp.route("/area")
@login_required
def area_list():
    daftar_area = AreaParkir.query.order_by(AreaParkir.nama_area.asc()).all()
    return render_template("admin/area_list.html", daftar_area=daftar_area)


@admin_bp.route("/area/tambah", methods=["GET", "POST"])
@login_required
def area_tambah():
    if request.method == "POST":
        nama_area = request.form.get("nama_area", "").strip()
        lokasi = request.form.get("lokasi", "").strip()
        kapasitas = request.form.get("kapasitas", "").strip()
        keterangan = request.form.get("keterangan", "").strip()

        errors = []
        if not nama_area:
            errors.append("Nama area wajib diisi.")
        elif AreaParkir.query.filter_by(nama_area=nama_area).first():
            errors.append("Nama area sudah digunakan.")
        if not kapasitas.isdigit() or int(kapasitas) <= 0:
            errors.append("Kapasitas harus berupa angka lebih dari 0.")

        if errors:
            for e in errors:
                flash(e, "danger")
            return render_template("admin/area_form.html", mode="tambah", area=None)

        db.session.add(AreaParkir(
            nama_area=nama_area, lokasi=lokasi or None,
            kapasitas=int(kapasitas), keterangan=keterangan or None,
        ))
        db.session.commit()
        flash("Area parkir baru berhasil ditambahkan.", "success")
        return redirect(url_for("admin.area_list"))

    return render_template("admin/area_form.html", mode="tambah", area=None)


@admin_bp.route("/area/<int:area_id>/edit", methods=["GET", "POST"])
@login_required
def area_edit(area_id):
    area = AreaParkir.query.get_or_404(area_id)

    if request.method == "POST":
        nama_area = request.form.get("nama_area", "").strip()
        lokasi = request.form.get("lokasi", "").strip()
        kapasitas = request.form.get("kapasitas", "").strip()
        keterangan = request.form.get("keterangan", "").strip()

        errors = []
        if not nama_area:
            errors.append("Nama area wajib diisi.")
        else:
            duplikat = AreaParkir.query.filter(
                AreaParkir.nama_area == nama_area, AreaParkir.id != area_id
            ).first()
            if duplikat:
                errors.append("Nama area sudah digunakan area lain.")
        if not kapasitas.isdigit() or int(kapasitas) <= 0:
            errors.append("Kapasitas harus berupa angka lebih dari 0.")
        elif int(kapasitas) < area.terpakai:
            errors.append(
                f"Kapasitas tidak boleh lebih kecil dari jumlah kendaraan yang sedang parkir ({area.terpakai})."
            )

        if errors:
            for e in errors:
                flash(e, "danger")
            return render_template("admin/area_form.html", mode="edit", area=area)

        area.nama_area = nama_area
        area.lokasi = lokasi or None
        area.kapasitas = int(kapasitas)
        area.keterangan = keterangan or None
        db.session.commit()
        flash("Data area parkir berhasil diperbarui.", "success")
        return redirect(url_for("admin.area_list"))

    return render_template("admin/area_form.html", mode="edit", area=area)


@admin_bp.route("/area/<int:area_id>/hapus", methods=["POST"])
@login_required
def area_hapus(area_id):
    area = AreaParkir.query.get_or_404(area_id)
    db.session.delete(area)
    db.session.commit()
    flash("Area parkir berhasil dihapus.", "success")
    return redirect(url_for("admin.area_list"))


# ---------- TRANSAKSI PARKIR (CHECK-IN / CHECK-OUT) ----------

@admin_bp.route("/transaksi")
@login_required
def transaksi_list():
    status = request.args.get("status", "")
    query = Transaksi.query
    if status in STATUS_TRANSAKSI:
        query = query.filter_by(status=status)
    daftar_transaksi = query.order_by(Transaksi.waktu_masuk.desc()).all()
    return render_template(
        "admin/transaksi_list.html", daftar_transaksi=daftar_transaksi,
        status=status, status_list=STATUS_TRANSAKSI,
    )


@admin_bp.route("/transaksi/checkin", methods=["GET", "POST"])
@login_required
def transaksi_checkin():
    daftar_kendaraan = Kendaraan.query.order_by(Kendaraan.plat_nomor.asc()).all()
    daftar_area = AreaParkir.query.order_by(AreaParkir.nama_area.asc()).all()

    if request.method == "POST":
        kendaraan_id = request.form.get("kendaraan_id", "")
        area_id = request.form.get("area_id", "")
        petugas = request.form.get("petugas", "").strip()
        catatan = request.form.get("catatan", "").strip()

        errors = []
        kendaraan = Kendaraan.query.get(kendaraan_id) if kendaraan_id.isdigit() else None
        area = AreaParkir.query.get(area_id) if area_id.isdigit() else None

        if not kendaraan:
            errors.append("Kendaraan wajib dipilih.")
        elif kendaraan.sedang_parkir:
            errors.append("Kendaraan ini masih tercatat sedang parkir (belum check-out).")
        if not area:
            errors.append("Area parkir wajib dipilih.")
        elif area.penuh:
            errors.append(f"Area {area.nama_area} sudah penuh, pilih area lain.")
        if not petugas:
            errors.append("Nama petugas wajib diisi.")

        if errors:
            for e in errors:
                flash(e, "danger")
            return render_template(
                "admin/transaksi_form.html", daftar_kendaraan=daftar_kendaraan,
                daftar_area=daftar_area,
            )

        db.session.add(Transaksi(
            kendaraan_id=kendaraan.id, area_id=area.id,
            waktu_masuk=datetime.utcnow(), status="Masih Parkir",
            petugas=petugas, catatan=catatan or None,
        ))
        db.session.commit()
        flash(f"Kendaraan {kendaraan.plat_nomor} berhasil check-in di {area.nama_area}.", "success")
        return redirect(url_for("admin.transaksi_list"))

    return render_template(
        "admin/transaksi_form.html", daftar_kendaraan=daftar_kendaraan, daftar_area=daftar_area,
    )


@admin_bp.route("/transaksi/<int:transaksi_id>/checkout", methods=["POST"])
@login_required
def transaksi_checkout(transaksi_id):
    transaksi = Transaksi.query.get_or_404(transaksi_id)
    if transaksi.status == "Masih Parkir":
        transaksi.waktu_keluar = datetime.utcnow()
        transaksi.status = "Sudah Keluar"
        db.session.commit()
        flash("Kendaraan berhasil check-out.", "success")
    else:
        flash("Transaksi ini sudah check-out sebelumnya.", "danger")
    return redirect(url_for("admin.transaksi_list"))


@admin_bp.route("/transaksi/<int:transaksi_id>/hapus", methods=["POST"])
@login_required
def transaksi_hapus(transaksi_id):
    transaksi = Transaksi.query.get_or_404(transaksi_id)
    db.session.delete(transaksi)
    db.session.commit()
    flash("Data transaksi berhasil dihapus.", "success")
    return redirect(url_for("admin.transaksi_list"))
