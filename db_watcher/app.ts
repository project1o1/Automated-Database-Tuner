import { Client } from "pg";
import express from "express";
const app = express();
const PORT = 3000;

app.use(express.json());
const connectionConfig = {
  user: "postgres",
  password: "1234",
  host: "127.0.0.1",
  database: "target_db",
  port: 5432,
};

const client = new Client(connectionConfig);
client.connect();

app.post("/cost", (req, res) => {
  const { query, indexes } = req.body;
});

app.post("/addIndex", (req, res) => {
  const { indexes } = req.body;
});

app.post("/deleteIndex", (req, body) => {
  const { indexes } = req.body;
});

app.listen(PORT, (error: Error) => {
  if (!error)
    console.log(
      "Server is Successfully Running, and App is listening on port " + PORT
    );
  else console.log("Error occurred, server can't start", error);
});
