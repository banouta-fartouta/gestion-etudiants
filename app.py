import os
from flask import Flask, flash, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-key-change-later")
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///etudiants.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


class Etudiant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    prenom = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(200), unique=True, nullable=False)
    filiere = db.Column(db.String(100), nullable=False)


with app.app_context():
    db.create_all()


@app.get("/")
def index():
    etudiants = db.session.execute(db.select(Etudiant).order_by(Etudiant.id)).scalars().all()
    return render_template("index.html", etudiants=etudiants)


@app.post("/ajouter")
def ajouter():
    nom = request.form.get("nom", "").strip()
    prenom = request.form.get("prenom", "").strip()
    email = request.form.get("email", "").strip().lower()
    filiere = request.form.get("filiere", "").strip()
    if not all([nom, prenom, email, filiere]):
        flash("Tous les champs sont obligatoires.", "error")
        return redirect(url_for("index"))
    db.session.add(Etudiant(nom=nom, prenom=prenom, email=email, filiere=filiere))
    try:
        db.session.commit()
        flash("Étudiant ajouté avec succès.", "success")
    except IntegrityError:
        db.session.rollback()
        flash("Cet e-mail existe déjà.", "error")
    return redirect(url_for("index"))


@app.post("/modifier/<int:etudiant_id>")
def modifier(etudiant_id):
    etudiant = db.get_or_404(Etudiant, etudiant_id)
    nom = request.form.get("nom", "").strip()
    prenom = request.form.get("prenom", "").strip()
    email = request.form.get("email", "").strip().lower()
    filiere = request.form.get("filiere", "").strip()
    if not all([nom, prenom, email, filiere]):
        flash("Tous les champs sont obligatoires.", "error")
        return redirect(url_for("index"))
    etudiant.nom, etudiant.prenom, etudiant.email, etudiant.filiere = nom, prenom, email, filiere
    try:
        db.session.commit()
        flash("Étudiant modifié avec succès.", "success")
    except IntegrityError:
        db.session.rollback()
        flash("Cet e-mail existe déjà.", "error")
    return redirect(url_for("index"))


@app.post("/supprimer/<int:etudiant_id>")
def supprimer(etudiant_id):
    etudiant = db.get_or_404(Etudiant, etudiant_id)
    db.session.delete(etudiant)
    db.session.commit()
    flash("Étudiant supprimé.", "success")
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)

