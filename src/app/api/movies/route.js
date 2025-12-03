import { getDB } from "@/lib/db";

export async function GET(request) {
  try {
    const db = await getDB();
    const { searchParams } = new URL(request.url);
    
    // Get filter parameters
    const genre = searchParams.get("genre");
    const maxRating = searchParams.get("maxRating");
    const minRuntime = searchParams.get("minRuntime");
    const maxRuntime = searchParams.get("maxRuntime");
    const yearFrom = searchParams.get("yearFrom");
    const yearTo = searchParams.get("yearTo");
    const minRating = searchParams.get("minRating");
    const minVotes = searchParams.get("minVotes");
    const titleSearch = searchParams.get("titleSearch");
    const sortBy = searchParams.get("sortBy") || "rating";
    const actors = searchParams.get("actors")?.split(",").filter(Boolean) || [];
    const limitParam = searchParams.get("limit");
    const limit = limitParam ? Math.max(1, Math.min(500, parseInt(limitParam) || 100)) : 100;

    // Build the query - start simple and only add filters that actually restrict
    let query = "SELECT * FROM all_raw WHERE 1=1";
    const params = [];

    // Title search filter
    if (titleSearch && titleSearch.trim() !== "") {
      query += " AND title LIKE ?";
      params.push(`%${titleSearch.trim()}%`);
    }

    // Genre filter (check if genre string contains the selected genre)
    // If no genre is specified, show all movies
    if (genre && genre !== "" && genre !== "Any") {
      query += " AND genre LIKE ?";
      params.push(`%${genre}%`);
    }

    // Certificate/Rating filter - make it very lenient
    // Only filter if certificate exists and doesn't match, otherwise allow through
    if (maxRating) {
      const ratingOrder = { G: 1, PG: 2, "PG-13": 3, R: 4, "NC-17": 5 };
      const maxRatingValue = ratingOrder[maxRating] || 4;
      const allowedRatings = Object.keys(ratingOrder)
        .filter(r => ratingOrder[r] <= maxRatingValue);
      
      if (allowedRatings.length > 0) {
        // Build a more lenient filter - allow NULL, empty, or any of the allowed ratings
        const ratingList = allowedRatings.map(r => `'${r.replace(/'/g, "''")}'`).join(",");
        query += ` AND (certificate IS NULL OR certificate = '' OR certificate IN (${ratingList}))`;
      }
    }

    // Runtime filter - filter for movies with duration <= maxRuntime
    // Allow NULL/empty durations through (don't filter them out)
    if (maxRuntime) {
      query += " AND (duration IS NULL OR duration = '' OR CAST(COALESCE(duration, 0) AS UNSIGNED) <= ?)";
      params.push(parseInt(maxRuntime));
    }
    if (minRuntime) {
      query += " AND (duration IS NULL OR duration = '' OR CAST(COALESCE(duration, 0) AS UNSIGNED) >= ?)";
      params.push(parseInt(minRuntime));
    }

    // Year filter - be more lenient, only filter if year is actually set and valid
    // Don't filter out NULL years since many movies might not have year data
    if (yearFrom && yearFrom > 0) {
      query += " AND (year IS NULL OR year = 0 OR year >= ?)";
      params.push(parseInt(yearFrom));
    }
    if (yearTo && yearTo > 0 && yearTo < 3000) {
      query += " AND (year IS NULL OR year = 0 OR year <= ?)";
      params.push(parseInt(yearTo));
    }

    // IMDB Rating filter
    if (minRating && parseFloat(minRating) > 0) {
      query += " AND rating >= ?";
      params.push(parseFloat(minRating));
    }

    // Minimum votes filter (popularity)
    if (minVotes && parseInt(minVotes) > 0) {
      query += " AND votes >= ?";
      params.push(parseInt(minVotes));
    }

    // Actor filter (check if stars field contains actor name)
    if (actors.length > 0) {
      const actorConditions = actors.map(() => "stars LIKE ?").join(" OR ");
      query += ` AND (${actorConditions})`;
      actors.forEach(actor => {
        params.push(`%${actor}%`);
      });
    }

    // Order by based on sortBy parameter
    switch (sortBy) {
      case "votes":
        query += " ORDER BY votes DESC, rating DESC LIMIT ?";
        break;
      case "year":
        query += " ORDER BY year DESC, rating DESC LIMIT ?";
        break;
      case "year_old":
        query += " ORDER BY year ASC, rating DESC LIMIT ?";
        break;
      case "runtime":
        query += " ORDER BY duration ASC, rating DESC LIMIT ?";
        break;
      case "runtime_long":
        query += " ORDER BY duration DESC, rating DESC LIMIT ?";
        break;
      case "rating":
      default:
        query += " ORDER BY rating DESC, votes DESC LIMIT ?";
        break;
    }
    params.push(limit);

    console.log("Executing query:", query);
    console.log("With params:", params);
    
    const [rows] = await db.query(query, params);
    
    console.log(`Found ${rows.length} movies`);
    
    // Debug: If no results, test simpler queries to find the issue
    if (rows.length === 0) {
      console.log("=== DEBUGGING: No results found ===");
      
      // Test 1: Simple query with no filters
      const [test1] = await db.query("SELECT COUNT(*) as count FROM all_raw");
      console.log("1. Total rows in table:", test1[0]?.count || 0);
      
      // Test 2: Check if genre filter works
      if (genre && genre !== "" && genre !== "Any") {
        const [test2] = await db.query("SELECT COUNT(*) as count FROM all_raw WHERE genre LIKE ?", [`%${genre}%`]);
        console.log(`2. Rows with genre containing "${genre}":`, test2[0]?.count || 0);
      }
      
      // Test 3: Check year data
      const [test3] = await db.query("SELECT COUNT(*) as count FROM all_raw WHERE year IS NOT NULL AND year > 0");
      console.log("3. Rows with valid year:", test3[0]?.count || 0);
      
      // Test 4: Sample data
      const [test4] = await db.query("SELECT title, genre, certificate, year, duration FROM all_raw LIMIT 3");
      console.log("4. Sample rows:", JSON.stringify(test4, null, 2));
    }

    // Transform the data to match the UI format
    const movies = rows.map(row => {
      // Parse genres (might be comma-separated)
      const genres = row.genre 
        ? row.genre.split(",").map(g => g.trim()).filter(Boolean)
        : [];
      
      // Parse stars/cast - handle different formats
      let cast = [];
      if (row.stars) {
        try {
          // Handle both comma-separated and other formats
          let starsStr = String(row.stars).trim();
          
          // Remove any array-like brackets if present
          starsStr = starsStr.replace(/^\[|\]$/g, '');
          
          // Split by comma and clean up each name
          cast = starsStr
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
                     s !== "Documentary" && 
                     s !== "N/A" && 
                     !s.match(/^['"\[\]]+$/) && // Not just brackets/quotes
                     s.length < 100; // Reasonable name length
            })
            .slice(0, 3);
        } catch (err) {
          console.error("Error parsing cast:", err, row.stars);
          cast = [];
        }
      }

      // Map certificate to rating format
      const rating = row.certificate || "Unrated";

      // Parse duration - handle different formats (string, number, etc.)
      let runtime = 0;
      if (row.duration) {
        const durationStr = String(row.duration).trim();
        // Try to extract number from string (e.g., "120 min" -> 120)
        const durationMatch = durationStr.match(/(\d+)/);
        if (durationMatch) {
          runtime = parseInt(durationMatch[1]);
        } else {
          runtime = parseInt(durationStr) || 0;
        }
      }

      return {
        title: row.title || "Unknown",
        genres: genres,
        runtime: runtime,
        rating: rating,
        score: parseFloat(row.rating) || 0,
        synopsis: row.description || "No description available.",
        cast: cast,
        director: "Unknown", // Not in all_raw table
        year: row.year || null,
        votes: row.votes || 0,
        rating_value: parseFloat(row.rating) || 0
      };
    });

    return Response.json({
      success: true,
      movies: movies,
      count: movies.length
    });

  } catch (error) {
    console.error("Database error:", error);
    return Response.json({
      success: false,
      error: error.message,
      stack: process.env.NODE_ENV === "development" ? error.stack : undefined
    }, { status: 500 });
  }
}

