from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "static/uploads"

# ---------------- DATABASE ----------------
def create_database():
    conn = sqlite3.connect("microscope.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS calculations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        measured_size REAL,
        real_size REAL
    )
    """)

    conn.commit()
    conn.close()

def save_record(username, measured, real):
    conn = sqlite3.connect("microscope.db")
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO calculations (username, measured_size, real_size)
    VALUES (?, ?, ?)
    """, (username, measured, real))

    conn.commit()
    conn.close()

def get_records():
    conn = sqlite3.connect("microscope.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM calculations")
    data = cursor.fetchall()
    conn.close()
    return data

def delete_record(record_id):
    conn = sqlite3.connect("microscope.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM calculations WHERE id=?", (record_id,))
    conn.commit()
    conn.close()

# ---------------- DATA ----------------
microscopes = {
    "Light Microscope": 1000,
    "SEM": 100000,
    "TEM": 1000000,
    "Stereo Microscope": 50
}

units = {
    "nm": 1e6,
    "µm": 1e3,
    "mm": 1,
    "cm": 0.1,
    "m": 0.001
}

# ---------------- ROUTES ----------------
@app.route("/", methods=["GET", "POST"])
def index():
    result = None

    if request.method == "POST":
        username = request.form["username"]
        measured = float(request.form["measured"])
        microscope = request.form["microscope"]
        unit = request.form["unit"]

        # Handle image upload
        file = request.files["image"]
        if file:
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
            file.save(filepath)

        magnification = microscopes[microscope]
        factor = units[unit]

        real_mm = measured / magnification
        final = real_mm * factor

        result = {
            "username": username,
            "measured": measured,
            "microscope": microscope,
            "real_mm": real_mm,
            "final": final,
            "unit": unit,
            "factor": factor,
            "magnification": magnification
        }

        save_record(username, measured, real_mm)

    return render_template("index.html", microscopes=microscopes, units=units, result=result)


@app.route("/records")
def records():
    data = get_records()
    return render_template("records.html", records=data)


@app.route("/delete/<int:id>")
def delete(id):
    delete_record(id)
    return redirect(url_for("records"))


# ---------------- RUN ----------------
if __name__ == "__main__":
    create_database()
    app.run(debug=True)