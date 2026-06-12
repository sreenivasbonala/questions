from flask import Flask, jsonify, request, render_template
import sqlite3

app = Flask(__name__)
DATABASE = "analysis.db"


def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def create_table():
    conn = get_db_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS sequence_analysis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sequence_id TEXT NOT NULL,
            organism TEXT NOT NULL,
            sequence TEXT NOT NULL,
            analysis_result TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/results", methods=["POST"])
def add_result():
    data = request.get_json()

    conn = get_db_connection()
    conn.execute("""
        INSERT INTO sequence_analysis
        (sequence_id, organism, sequence, analysis_result)
        VALUES (?, ?, ?, ?)
    """, (
        data["sequence_id"],
        data["organism"],
        data["sequence"],
        data["analysis_result"]
    ))

    conn.commit()
    conn.close()

    return jsonify({"message": "Sequence analysis result added successfully"})


@app.route("/api/results", methods=["GET"])
def get_results():
    conn = get_db_connection()
    results = conn.execute("SELECT * FROM sequence_analysis").fetchall()
    conn.close()

    return jsonify([dict(row) for row in results])


@app.route("/api/results/<int:id>", methods=["GET"])
def get_result_by_id(id):
    conn = get_db_connection()
    result = conn.execute(
        "SELECT * FROM sequence_analysis WHERE id = ?",
        (id,)
    ).fetchone()
    conn.close()

    if result is None:
        return jsonify({"error": "Result not found"}), 404

    return jsonify(dict(result))


if __name__ == "__main__":
    create_table()
    app.run(debug=True)