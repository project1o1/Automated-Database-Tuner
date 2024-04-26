import { Client } from "pg";
import axios from "axios";
function parseSqlParams(sql: string): { [key: string]: string } {
  const params: { [key: string]: string } = {};

  // Extract selected columns
  const match = sql.match(/SELECT (.*?) FROM/);
  if (match) {
    params.selectedColumns = match[1].trim();
  }

  // Extract WHERE clause (if exists)
  if (sql.includes("WHERE")) {
    const whereClause = sql.split("WHERE")[1].trim();

    // Extract comparison operator and value
    const match = whereClause.match(/(\w+)\s*(=|>|<|>=|<=|!=)\s*(.*)/);
    if (match) {
      params.column = match[1].trim();
      params.operator = match[2].trim();
      params.value = match[3].trim();
      // Remove single quotes from string values
      if (params.value.startsWith("'") && params.value.endsWith("'")) {
        params.value = params.value.slice(1, -1);
      }
    }
  }

  return params;
}

// Example usage
const sql = "SELECT username, email FROM users WHERE user_id > 100";
const parsedParams = parseSqlParams(sql);
console.log(parsedParams); // { selectedColumns: 'username, email', column: 'user_id', operator: '>', value: '100' }

export default async function createWatcher() {
  const connectionConfig = {
    user: "postgres",
    password: "1234",
    host: "127.0.0.1",
    database: "target_db",
    port: 5432,
  };

  const client = new Client(connectionConfig);
  await client.connect();

  const tmp = async () => {
    try {
      const res = await client.query(
        "select query, mean_exec_time from pg_stat_statements "
      );
      res.rows.forEach(async (row) => {
        try {
          let parsed = parseSqlParams(row.query);
          console.log(parsed);
          if (parsed["column"] == undefined) return;
          const sent = {
            query: row.query,
            columns: parsed["column"],
            cost: row.mean_exec_time,
          };
          console.log(sent);
          await axios.get(
            `http://172.16.14.230:8000/new_query?query=${sent.query}&columns=${sent.columns}&cost=${sent.cost}`
          );
        } catch (e) {}
      });
      await client.query("select pg_stat_statements_reset()");
    } catch (e) {
      console.log("not expected");
      console.log(e);
    }
  };
  while (true) {
    tmp();
    await new Promise((resolve) => setTimeout(resolve, 1000));
  }
}

createWatcher();
