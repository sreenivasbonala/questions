const express = require("express");
const db = require("./database");

const app = express();
const PORT = 3000;

app.use(express.json());
app.use(express.static("public"));

app.post("/registrations", (req, res) => {
    const { id, student_name, course_name, email, semester } = req.body;

    db.run(
        `INSERT INTO courses 
        (id, student_name, course_name, email, semester)
        VALUES (?, ?, ?, ?, ?)`,
        [id, student_name, course_name, email, semester],
        (err) => {
            if (err) {
                return res.send("Error adding registration");
            }

            res.send("Course registered successfully");
        }
    );
});

app.get("/registrations", (req, res) => {
    db.all("SELECT * FROM courses", [], (err, rows) => {
        if (err) {
            return res.send("Error retrieving registrations");
        }

        res.json(rows);
    });
});

app.put("/registrations/:id", (req, res) => {
    const id = req.params.id;
    const { student_name, course_name, email, semester } = req.body;

    db.run(
        `UPDATE courses
        SET student_name=?,
            course_name=?,
            email=?,
            semester=?
        WHERE id=?`,
        [student_name, course_name, email, semester, id],
        (err) => {
            if (err) {
                return res.send("Error updating registration");
            }

            res.send("Registration updated successfully");
        }
    );
});

app.delete("/registrations/:id", (req, res) => {
    const id = req.params.id;

    db.run(
        "DELETE FROM courses WHERE id=?",
        [id],
        (err) => {
            if (err) {
                return res.send("Error deleting registration");
            }

            res.send("Registration deleted successfully");
        }
    );
});

app.listen(PORT, () => {
    console.log(`Server running on http://localhost:${PORT}`);
});