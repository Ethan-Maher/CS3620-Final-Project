import { getDB } from "@/lib/db";

export async function GET() {
  try {
    const db = await getDB();

    // try a simple query
    const [rows] = await db.query("SELECT 1 + 1 AS result");

    return Response.json({
      connected: true,
      testQuery: rows
    });

  } catch (error) {
    return Response.json({
      connected: false,
      error: error.message,
      stack: error.stack
    }, { status: 500 });
  }
}
