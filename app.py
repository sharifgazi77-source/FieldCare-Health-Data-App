import csv
import io
import os
from datetime import datetime
from flask import Flask, Response, flash, redirect, render_template, request, url_for
from sqlalchemy import create_engine, text

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "fieldcare-local-change-me")
DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    DATABASE_URL = "sqlite:///" + os.path.join(os.path.dirname(__file__), "fieldcare.db").replace("\\", "/")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg://", 1)
elif DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg://", 1)
engine = create_engine(DATABASE_URL)
DEPARTMENTS = ["Doctor", "Nurse", "Social Work", "Psychologist", "Psychiatrist", "Pharmacy", "Midwife", "Gynecologist", "Other"]
LANGUAGES = ["বাংলা", "English", "العربية", "Français", "Kurdish", "اردو", "فارسی", "Other"]

def init_db():
    id_type = "SERIAL PRIMARY KEY" if engine.dialect.name == "postgresql" else "INTEGER PRIMARY KEY AUTOINCREMENT"
    with engine.begin() as con:
        con.execute(text(f"""CREATE TABLE IF NOT EXISTS records (
            id {id_type}, created_at TEXT NOT NULL,
            patient_name TEXT, language TEXT, nationality TEXT, department TEXT,
            people INTEGER, male INTEGER, female INTEGER, topic TEXT, notes TEXT)"""))

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        form = request.form
        kind = form.get("record_type", "patient")
        patient = form.get("patient_name", "").strip()
        language = form.get("language", "").strip()
        nationality = form.get("nationality", "").strip()
        department = form.get("department", "").strip()
        topic = form.get("topic", "").strip()
        notes = form.get("notes", "").strip()
        try:
            people = int(form.get("people") or 0)
            male = int(form.get("male") or 0)
            female = int(form.get("female") or 0)
            if min(people, male, female) < 0: raise ValueError
        except ValueError:
            flash("সংখ্যার ঘরে শূন্য বা তার বেশি পূর্ণসংখ্যা লিখুন।", "error")
            return redirect(url_for("home", tab=kind))
        if kind == "patient" and (not patient or not language or not nationality or department not in DEPARTMENTS):
            flash("রোগীর নাম, ভাষা, জাতীয়তা ও বিভাগ পূরণ করুন।", "error")
            return redirect(url_for("home", tab=kind))
        if kind == "education" and (people < 1 or not topic):
            flash("অংশগ্রহণকারীর সংখ্যা ও সেশনের বিষয় পূরণ করুন।", "error")
            return redirect(url_for("home", tab=kind))
        if kind == "education" and male + female > people:
            flash("পুরুষ ও নারীর যোগফল মোট অংশগ্রহণকারীর চেয়ে বেশি হতে পারবে না।", "error")
            return redirect(url_for("home", tab=kind))
        if kind == "extra" and not notes:
            flash("অতিরিক্ত কাজ বা নোট লিখুন।", "error")
            return redirect(url_for("home", tab=kind))
        with engine.begin() as con:
            con.execute(text("INSERT INTO records (created_at, patient_name, language, nationality, department, people, male, female, topic, notes) VALUES (:created_at,:patient_name,:language,:nationality,:department,:people,:male,:female,:topic,:notes)"),
                        dict(created_at=datetime.now().astimezone().isoformat(timespec="minutes"), patient_name=patient or None, language=language or None, nationality=nationality or None, department=department or None,
                             people=people if kind == "education" else None, male=male if kind == "education" else None, female=female if kind == "education" else None, topic=topic or None, notes=notes or None))
        flash("তথ্য সফলভাবে সংরক্ষণ হয়েছে।", "success")
        return redirect(url_for("home", tab=kind))
    with engine.connect() as con:
        records = con.execute(text("SELECT * FROM records ORDER BY id DESC LIMIT 12")).mappings().all()
        total = con.execute(text("SELECT COUNT(*) FROM records")).scalar_one()
    return render_template("index.html", records=records, total=total, departments=DEPARTMENTS, languages=LANGUAGES, active=request.args.get("tab", "patient"))

@app.get("/export.csv")
def export_csv():
    with engine.connect() as con: records = con.execute(text("SELECT * FROM records ORDER BY id DESC")).mappings().all()
    output = io.StringIO(); writer = csv.writer(output)
    writer.writerow(["ID", "Created", "Patient Name", "Language", "Nationality", "Department", "Participants", "Male", "Female", "Topic", "Extra Tasks / Notes"])
    for row in records: writer.writerow(list(row.values()))
    return Response("\ufeff" + output.getvalue(), mimetype="text/csv; charset=utf-8", headers={"Content-Disposition": "attachment; filename=fieldcare-records.csv"})

@app.post("/delete/<int:record_id>")
def delete_record(record_id):
    with engine.begin() as con: con.execute(text("DELETE FROM records WHERE id=:id"), {"id": record_id})
    flash("রেকর্ড মুছে ফেলা হয়েছে।", "success")
    return redirect(url_for("home"))

init_db()
if _name_ == '_main_':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
