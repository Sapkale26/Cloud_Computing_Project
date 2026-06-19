require("dotenv").config();

const express = require("express");
const pool = require("./db");

const app = express();

app.use(express.json());

app.get("/", (req, res) => {
  res.send("Backend connected to PostgreSQL");
});

app.post("/events", async (req, res) => {
  try {
    const { event_type, location, image_url } = req.body;

    const result = await pool.query(
      "INSERT INTO events (event_type, location, image_url) VALUES ($1, $2, $3) RETURNING *",
      [event_type, location, image_url]
    );

    res.json({
      message: "Event added successfully",
      event: result.rows[0],
    });
  } catch (error) {
    console.error(error);
    res.status(500).json({ error: "Database error" });
  }
});

app.get("/events", async (req, res) => {
  try {
    const result = await pool.query("SELECT * FROM events ORDER BY created_at DESC");
    res.json(result.rows);
  } catch (error) {
    console.error(error);
    res.status(500).json({ error: "Database error" });
  }
});

app.listen(3000, () => {
  console.log("Server started on port 3000");
});