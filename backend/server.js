const express = require("express");

const app = express();

app.use(express.json());

let events = [];

app.get("/", (req, res) => {
    res.send("Backend Running");
});

app.post("/events", (req, res) => {

    console.log(req.body);

    events.push(req.body);

    res.send("Event Added");
});

app.get("/events", (req, res) => {

    res.json(events);

});

app.listen(3000, () => {
    console.log("Server started!");
});