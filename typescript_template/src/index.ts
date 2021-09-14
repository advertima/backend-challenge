import express from "express";
import knex from "knex";
import process from 'process';

const app = express();
const port = 8000;

// Feel free to replace with the ORM of your choice
export const knexClient = knex({
  client: "sqlite3",
  connection: ":memory:",
  useNullAsDefault: true,
});

knexClient.schema.createTable("my_table", (table) => {
  table.increments();
  table.timestamp("time").notNullable();
}).then();


app.get("/", async (req, res) => {
  res.send({ service: "Timeline API" });
});

app.post("/enter_event", (req, res) => {
  // TODO
  res.send({});
});

app.post("/exit_event", (req, res) => {
  // TODO
  res.send({});
});

app.get("/timeline/:tracking_id", (req, res) => {
  // TODO
  res.send([]);
});

app.listen(port, () => {
  console.log(`App listening at http://localhost:${port}`);
});


process.on('SIGINT', () => {
  process.exit(0);
});
