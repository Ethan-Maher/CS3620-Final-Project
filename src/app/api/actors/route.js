import { getDB } from "@/lib/db";

export async function GET() {
  try {
    const db = await getDB();
    
    // Get all unique actors from the stars field
    const [rows] = await db.query(
      "SELECT DISTINCT stars FROM all_raw WHERE stars IS NOT NULL AND stars != '' LIMIT 2000"
    );

    // Parse and collect all unique actors with proper cleaning
    const actorSet = new Set();
    rows.forEach(row => {
      if (row.stars) {
        try {
          // Handle both comma-separated and other formats
          let starsStr = String(row.stars).trim();
          
          // Remove any array-like brackets if present
          starsStr = starsStr.replace(/^\[|\]$/g, '');
          
          // Split by comma and clean up each name
          const actors = starsStr
            .split(",")
            .map(s => {
              // Remove quotes, brackets, and trim
              let cleaned = s.trim()
                .replace(/^['"\[\]]+|['"\[\]]+$/g, '')
                .replace(/^['"]+|['"]+$/g, '')
                .trim();
              return cleaned;
            })
            .filter(s => {
              // Filter out invalid entries
              return s.length > 0 && 
                     s.length >= 2 && 
                     s.length < 50 &&
                     s !== "Documentary" && 
                     s !== "N/A" && 
                     !s.match(/^['"\[\]]+$/) && // Not just brackets/quotes
                     !s.match(/^\d+$/) && // Not just numbers
                     !s.toLowerCase().includes("documentary") &&
                     !s.toLowerCase().includes("n/a");
            });
          
          actors.forEach(actor => {
            if (actor && actor.length > 0) {
              actorSet.add(actor);
            }
          });
        } catch (err) {
          console.error("Error parsing actors:", err, row.stars);
        }
      }
    });

    const actors = Array.from(actorSet).sort().slice(0, 200); // Limit to top 200

    return Response.json({
      success: true,
      actors: actors
    });

  } catch (error) {
    console.error("Database error:", error);
    return Response.json({
      success: false,
      error: error.message
    }, { status: 500 });
  }
}
