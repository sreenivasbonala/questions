const sqlite3 = require("sqlite3").verbose();

const db = new sqlite3.Database("./courses.db", (err) => {
    if (err) {
        console.log(err.message);
    } else {
        console.log("Connected to SQLite database");
    }
});

db.run(`
CREATE TABLE IF NOT EXISTS courses (
    id INTEGER PRIMARY KEY,
    student_name TEXT NOT NULL,
    course_name TEXT NOT NULL,
    email TEXT NOT NULL,
    semester TEXT NOT NULL
)
`);

module.exports = db;