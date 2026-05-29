# Edge Computing Monitoring Backend

This project is part of a cloud computing and distributed systems seminar project.

## Current Progress

* Node.js backend setup
* Express.js server running
* REST API created
* POST API working
* GET API working
* Postman testing completed

---

# Technologies Used

* Node.js
* Express.js
* Postman
* GitHub

---

# API Endpoints

## GET /

Checks if backend is running.

## POST /events

Adds new event.

Example JSON:

```json
{
  "type": "fire",
  "location": "room 1"
}
```

## GET /events

Returns all stored events.

---

# How To Run Project

Install dependencies:

```bash
npm install
```

Run server:

```bash
node server.js
```

Server runs on:

```text
http://localhost:3000
```

---

# Author

PURVESH SHAPARIYA
SHUBHANGI SAPKALE
