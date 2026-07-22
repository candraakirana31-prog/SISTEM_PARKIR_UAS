from flask import Blueprint, render_template, request, redirect, url_for, session, flash

from models import Admin

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if session.get("admin_id"):
        return redirect(url_for("admin.dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not username or not password:
            flash("Username dan password wajib diisi.", "danger")
            return render_template("auth/login.html")

        admin = Admin.query.filter_by(username=username).first()

        if admin and admin.check_password(password):
            session["admin_id"] = admin.id
            session["admin_nama"] = admin.nama_lengkap
            flash(f"Selamat datang kembali, {admin.nama_lengkap}!", "success")
            return redirect(url_for("admin.dashboard"))

        flash("Username atau password salah.", "danger")

    return render_template("auth/login.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("Anda telah keluar dari sistem.", "success")
    return redirect(url_for("auth.login"))
