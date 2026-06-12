from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3
import os

app = Flask(__name__)

app.secret_key = "bioinformatics_secret_key"

UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Allows files up to 100 MB
app.config["MAX_CONTENT_LENGTH"] = 100 * 1024 * 1024

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


def get_db_connection():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn


def create_table():
    conn = get_db_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS fasta_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            filename TEXT,
            sequence_count INTEGER,
            sequence_length INTEGER,
            gc_content REAL
        )
    """)

    conn.execute("""
        INSERT OR IGNORE INTO users (id, username, password)
        VALUES (1, 'admin', 'admin123')
    """)

    conn.commit()
    conn.close()


create_table()


@app.route("/")
def home():
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        conn = get_db_connection()

        user = conn.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, password)
        ).fetchone()

        conn.close()

        if user:
            session["username"] = username
            return redirect(url_for("upload"))

        return "Invalid username or password"

    return render_template("login.html")


@app.route("/upload", methods=["GET", "POST"])
def upload():

    if "username" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":

        if "fasta_file" not in request.files:
            return "No file part found"

        file = request.files["fasta_file"]

        if file.filename == "":
            return "No file selected"

        if not file.filename.lower().endswith((".fasta", ".fa", ".txt")):
            return "Invalid file type. Upload .fasta, .fa, or .txt file"

        filepath = os.path.join(
            app.config["UPLOAD_FOLDER"],
            file.filename
        )

        file.save(filepath)

        try:
            sequence_count = 0
            total_length = 0
            gc_count = 0

            with open(filepath, "r") as f:
                for line in f:
                    line = line.strip().upper()

                    if line == "":
                        continue

                    if line.startswith(">"):
                        sequence_count += 1
                    else:
                        total_length += len(line)
                        gc_count += line.count("G") + line.count("C")

            if total_length == 0:
                return "Invalid FASTA file: no sequence found"

            gc_content = (gc_count / total_length) * 100

            conn = get_db_connection()

            conn.execute("""
                INSERT INTO fasta_results
                (username, filename, sequence_count, sequence_length, gc_content)
                VALUES (?, ?, ?, ?, ?)
            """, (
                session["username"],
                file.filename,
                sequence_count,
                total_length,
                gc_content
            ))

            conn.commit()
            conn.close()

            return redirect(url_for("results"))

        except Exception as e:
            return "Upload Error: " + str(e)

    return render_template("upload.html")


@app.route("/results")
def results():

    if "username" not in session:
        return redirect(url_for("login"))

    conn = get_db_connection()

    rows = conn.execute(
        "SELECT * FROM fasta_results WHERE username=?",
        (session["username"],)
    ).fetchall()

    conn.close()

    return render_template("results.html", results=rows)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.errorhandler(413)
def file_too_large(error):
    return "File too large. Please upload a FASTA file less than 100 MB.", 413


if __name__ == "__main__":
    app.run(debug=True)