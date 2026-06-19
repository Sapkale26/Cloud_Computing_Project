# Backend Setup

This document explains how the Node.js Express backend connects to PostgreSQL.

# Backend Setup

## Overview

The backend is developed using Node.js and Express.js.

The backend connects to PostgreSQL and provides REST APIs for storing and retrieving events.

## Technologies Used

* Node.js
* Express.js
* PostgreSQL
* pg
* dotenv

## Environment Configuration

`.env`

```env
DB_USER=postgres
DB_HOST=localhost
DB_NAME=edge_monitor
DB_PASSWORD=CloudProject2026!
DB_PORT=5432
```

## Database Connection

`db.js`

```javascript
const { Pool } = require("pg");

const pool = new Pool({
  user: process.env.DB_USER,
  host: process.env.DB_HOST,
  database: process.env.DB_NAME,
  password: process.env.DB_PASSWORD,
  port: process.env.DB_PORT,
});

module.exports = pool;
```

## API Endpoints

### GET /

Returns backend status.

### POST /events

Stores a new event in PostgreSQL.

Example:

```json
{
  "event_type": "Fire",
  "location": "Building A",
  "image_url": "fire.jpg"
}
```

### GET /events

Returns all stored events from the database.

## Testing

Tested using curl commands.

Insert Event:

```bash
curl -X POST http://localhost:3000/events
```

Get Events:

```bash
curl http://localhost:3000/events
```

## Result

Backend successfully communicates with PostgreSQL and stores event records.
