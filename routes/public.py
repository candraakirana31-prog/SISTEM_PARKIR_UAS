import os

from flask import Blueprint, render_template, current_app

from extensions import db
from models import Kendaraan, AreaParkir, Transaksi

public_bp = Blueprint("public", __name__)


@public_bp.route("/")
def index():
    total_kendaraan = Kendaraan.query.count()
    total_area = AreaParkir.query.count()
    sedang_parkir = Transaksi.query.filter_by(status="Masih Parkir").count()

    total_kapasitas = db.session.query(db.func.sum(AreaParkir.kapasitas)).scalar() or 0
    total_tersedia = max(total_kapasitas - sedang_parkir, 0)

    daftar_area = AreaParkir.query.order_by(AreaParkir.nama_area.asc()).all()

    return render_template(
        "pages/index.html",
        nama_kampus=current_app.config.get("NAMA_KAMPUS"),
        total_kendaraan=total_kendaraan,
        total_area=total_area,
        sedang_parkir=sedang_parkir,
        total_kapasitas=total_kapasitas,
        total_tersedia=total_tersedia,
        daftar_area=daftar_area,
    )


@public_bp.route("/debug-fs")
def debug_fs():
    root = current_app.root_path
    info = {
        "root_path": root,
        "root_contents": os.listdir(root),
        "templates_exists": os.path.isdir(os.path.join(root, "templates")),
    }
    if info["templates_exists"]:
        info["templates_contents"] = os.listdir(os.path.join(root, "templates"))
    return info