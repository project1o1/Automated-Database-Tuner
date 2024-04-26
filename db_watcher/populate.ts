import { Client, Pool } from "pg";
export default async function populateDb() {
  const connectionConfig = {
    user: "postgres",
    password: "1234",
    host: "127.0.0.1",
    database: "target_db",
    port: 5432,
  };

  const client = new Client(connectionConfig);
  await client.connect();

  // Function to generate a random string
  function generateRandomString(length: number): string {
    const characters =
      "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
    let result = "";
    for (let i = 0; i < length; i++) {
      result += characters.charAt(
        Math.floor(Math.random() * characters.length)
      );
    }
    return result;
  }

  // Function to generate a random email
  function generateRandomEmail(): string {
    return `${generateRandomString(10)}@example.com`;
  }

  async function populateUsersTable(pool: Pool) {
    // Define the number of random users to generate
    const numUsers = 10000000;
    const insertQuery = `INSERT INTO users (user_id, username, email, password, first_name, last_name, age) VALUES ($1, $2, $3, $4, $5, $6, $7)`;
    let start = 69;
    for (let i = 0; i < numUsers; i++) {
      let user = {
        user_id: start + i,
        username: generateRandomString(8),
        email: generateRandomEmail(),
        password: "hashed_password", // Replace with a placeholder for hashed password
        first_name: generateRandomString(12),
        last_name: generateRandomString(15),
        age: Math.floor(Math.random() * 70) + 18, // Generate age between 18 and 87
      };
      await pool.query(insertQuery, [
        user.user_id,
        user.username,
        user.email,
        user.password,
        user.first_name,
        user.last_name,
        user.age,
      ]);
    }

    // Insert users into the database
    console.log(`Successfully inserted ${numUsers} random users!`);
  }

  (async () => {
    try {
      const pool = new Pool(connectionConfig);
      await populateUsersTable(pool);
    } catch (error) {
      console.error("Error connecting to database:", error);
    } finally {
    }
  })();
}
populateDb();
