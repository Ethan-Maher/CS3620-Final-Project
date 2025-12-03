import { getDB } from "@/lib/db";

export async function GET() {
  try {
    const db = await getDB();
    
    // Get all unique genres from the database
    const [rows] = await db.query(
      "SELECT DISTINCT genre FROM all_raw WHERE genre IS NOT NULL AND genre != ''"
    );

    // Parse and collect all unique genres
    const genreSet = new Set();
    rows.forEach(row => {
      if (row.genre) {
        const genres = row.genre.split(",").map(g => g.trim()).filter(Boolean);
        genres.forEach(g => genreSet.add(g));
      }
    });

    const genres = Array.from(genreSet).sort();

    return Response.json({
      success: true,
      genres: genres
    });

  } catch (error) {
    console.error("Database error:", error);
    return Response.json({
      success: false,
      error: error.message
    }, { status: 500 });
  }
}

