import { Client } from "pg";
import fs from "fs";
type User = {
  user_id: number;
  username: string;
  email: string;
  password: string;
  first_name?: string; // Optional fields
  last_name?: string;
  age?: number;
};

function generateRandomSelectQueries(numQueries: number): string[] {
  const queries: string[] = [];

  for (let i = 0; i < numQueries; i++) {
    // Randomly choose selection type (all or specific columns)
    const selectType = Math.random() < 0.5 ? "*" : getRandomColumns();

    // Randomly choose WHERE clause or no WHERE clause
    const hasWhereClause = Math.random() < 0.5;
    let whereClause = "";

    if (hasWhereClause) {
      const randomColumn = getRandomColumn();
      const comparisonOperator = getRandomComparisonOperator();
      const randomValue = getRandomValue(getColumnType(randomColumn)); // Pass column type
      whereClause = ` WHERE ${randomColumn} ${comparisonOperator} ${randomValue}`;
    }

    const query = `SELECT ${selectType} FROM users ${whereClause}`;
    queries.push(query);
  }

  return queries;
}

function getRandomColumns(): string {
  const columns = [
    "user_id",
    "username",
    "email",
    "first_name",
    "last_name",
    "age",
  ];
  const numColumns = Math.floor(Math.random() * columns.length) + 1; // 1 to all columns
  const selectedColumns: any[] = [];
  for (let i = 0; i < numColumns; i++) {
    const randomIndex = Math.floor(Math.random() * columns.length);
    selectedColumns.push(columns[randomIndex]);
  }
  return selectedColumns.join(", ");
}

function getRandomColumn(): keyof User {
  // Use keyof to ensure valid column names
  const columns = [
    "user_id",
    "username",
    "email",
    "first_name",
    "last_name",
    "age",
  ];
  const randomIndex = Math.floor(Math.random() * columns.length);
  return columns[randomIndex] as keyof User;
}

function getRandomComparisonOperator(): string {
  const operators = ["=", ">", "<", ">=", "<=", "!="];
  const randomIndex = Math.floor(Math.random() * operators.length);
  return operators[randomIndex];
}

function getColumnType(columnName: keyof User): string {
  const types: { [key in keyof User]: string } = {
    user_id: "number",
    username: "string",
    email: "string",
    password: "string",
    first_name: "string", // Optional types can be string or undefined
    last_name: "string",
    age: "number",
  };
  return types[columnName]!;
}

function getRandomValue(columnType: string): string {
  // Improved random value generation based on column type
  switch (columnType) {
    case "number":
      return `${Math.floor(Math.random() * 1000)}`; // Generate random number
    case "string":
      const characters =
        "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
      const length = Math.floor(Math.random() * 10) + 1; // 1 to 10 characters
      let value = "";
      for (let i = 0; i < length; i++) {
        const randomIndex = Math.floor(Math.random() * characters.length);
        value += characters[randomIndex];
      }
      return `'${value}'`;
    default:
      throw new Error("Unsupported column type");
  }
}

const queries = generateRandomSelectQueries(10000);

console.log(queries); // This will print 10000 random select queries with type safety

const connectionConfig = {
  user: "postgres",
  password: "1234",
  host: "127.0.0.1",
  database: "target_db",
  port: 5432,
};
(async function () {
  const client = new Client(connectionConfig);
  await client.connect();

  for (let i = 0; i < queries.length; i++) {
    console.log(queries[i]);
    await client.query(queries[i]);
  }
})();

console.log(queries); // This will print 10000 random select queries
fs.writeFileSync("whatt.txt", JSON.stringify(queries));
