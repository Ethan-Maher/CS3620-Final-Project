"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { api } from "@/lib/api";
import Navbar from "@/components/Navbar";

export default function FavoritesPage() {
  const [favorites, setFavorites] = useState({
    fav_director: null,
    fav_director_name: null,
    fav_actor: "",
    fav_genre: null,
    fav_genre_name: null,
    fav_decade: "",
  });
  const [topRated, setTopRated] = useState({ top_movies: [], top_shows: [] });
  const [recommendations, setRecommendations] = useState([]);
  const [stats, setStats] = useState({
    total_reviews: 0,
    avg_rating: 0,
    top_genre: null,
  });
  const [genres, setGenres] = useState([]);
  const [activeTab, setActiveTab] = useState("preferences"); // preferences, top-rated, recommendations
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const router = useRouter();

  useEffect(() => {
    fetchAllData();
  }, []);

  const fetchAllData = async () => {
    setLoading(true);
    try {
      const user = JSON.parse(localStorage.getItem("user") || "{}");
      if (!user.user_id) {
        router.push("/signin");
        return;
      }

      await Promise.all([
        fetchFavorites(),
        fetchTopRated(),
        fetchRecommendations(),
        fetchGenres(),
      ]);
    } catch (err) {
      setError("Failed to load data");
    } finally {
      setLoading(false);
    }
  };

  const fetchFavorites = async () => {
    try {
      const response = await fetch(api.favorites, {
        credentials: "include",
      });
      const data = await response.json();
      if (data.success) {
        setFavorites(data.favorites || favorites);
      }
    } catch (err) {
      console.error("Error fetching favorites:", err);
    }
  };

  const fetchTopRated = async () => {
    try {
      const response = await fetch(api.userTopRated, {
        credentials: "include",
      });
      const data = await response.json();
      if (data.success) {
        setTopRated({
          top_movies: data.top_movies || [],
          top_shows: data.top_shows || [],
        });
        
        // Calculate stats
        const allRatings = [
          ...data.top_movies.map(m => m.rating),
          ...data.top_shows.map(s => s.rating)
        ];
        const totalReviews = allRatings.length;
        const avgRating = totalReviews > 0 
          ? (allRatings.reduce((a, b) => a + b, 0) / totalReviews).toFixed(1)
          : 0;
        
        // Get most common genre
        const genreCounts = {};
        [...data.top_movies, ...data.top_shows].forEach(item => {
          if (item.genre) {
            genreCounts[item.genre] = (genreCounts[item.genre] || 0) + 1;
          }
        });
        const topGenre = Object.keys(genreCounts).reduce((a, b) => 
          genreCounts[a] > genreCounts[b] ? a : b, null
        );
        
        setStats({
          total_reviews: totalReviews,
          avg_rating: avgRating,
          top_genre: topGenre,
        });
      }
    } catch (err) {
      console.error("Error fetching top rated:", err);
    }
  };

  const fetchRecommendations = async () => {
    try {
      const response = await fetch(api.personalizedRecommendations, {
        credentials: "include",
      });
      const data = await response.json();
      if (data.success) {
        setRecommendations(data.recommendations || []);
      }
    } catch (err) {
      console.error("Error fetching recommendations:", err);
    }
  };

  const fetchGenres = async () => {
    try {
      const response = await fetch(api.genres);
      const data = await response.json();
      if (data.success) {
        setGenres(data.genres || []);
      }
    } catch (err) {
      console.error("Error fetching genres:", err);
    }
  };

  const handleSave = async (e) => {
    e.preventDefault();
    setSaving(true);
    setError("");
    setSuccess("");

    try {
      const response = await fetch(api.favorites, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        credentials: "include",
        body: JSON.stringify({
          fav_director: favorites.fav_director,
          fav_actor: favorites.fav_actor,
          fav_genre: favorites.fav_genre,
          fav_decade: favorites.fav_decade,
        }),
      });

      const data = await response.json();
      if (data.success) {
        setFavorites(data.favorites);
        setSuccess("Favorites updated successfully! Refreshing recommendations...");
        setTimeout(() => {
          setSuccess("");
          fetchRecommendations();
        }, 2000);
      } else {
        setError(data.error || "Failed to update favorites");
      }
    } catch (err) {
      setError("Network error. Please try again.");
    } finally {
      setSaving(false);
    }
  };

  const decades = ["1990s", "2000s", "2010s", "2020s"];

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#0a0e1a] via-[#141827] to-[#0f1525] text-[#e8eaf6]">
      <Navbar 
        pageTitle="My Favorites"
        pageSubtitle="Your preferences and top picks"
      />

      <main className="mx-auto max-w-7xl px-6 py-8">
        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div className="rounded-xl bg-gradient-to-br from-[#141827]/80 to-[#0a0e1a]/60 border border-red-900/30 p-6 shadow-xl shadow-black/40 backdrop-blur-sm">
            <div className="text-sm text-gray-400 mb-1">Total Reviews</div>
            <div className="text-3xl font-bold text-red-400">{stats.total_reviews}</div>
          </div>
          <div className="rounded-xl bg-gradient-to-br from-[#141827]/80 to-[#0a0e1a]/60 border border-red-900/30 p-6 shadow-xl shadow-black/40 backdrop-blur-sm">
            <div className="text-sm text-gray-400 mb-1">Average Rating</div>
            <div className="text-3xl font-bold text-red-400">
              {stats.avg_rating > 0 ? `${stats.avg_rating}/10` : "N/A"}
            </div>
          </div>
          <div className="rounded-xl bg-gradient-to-br from-[#141827]/80 to-[#0a0e1a]/60 border border-red-900/30 p-6 shadow-xl shadow-black/40 backdrop-blur-sm">
            <div className="text-sm text-gray-400 mb-1">Top Genre</div>
            <div className="text-2xl font-bold text-red-400">{stats.top_genre || "None yet"}</div>
          </div>
        </div>

        {/* Tabs */}
        <div className="mb-6 flex gap-2 border-b border-red-900/20">
          <button
            onClick={() => setActiveTab("preferences")}
            className={`px-6 py-3 text-sm font-medium transition ${
              activeTab === "preferences"
                ? "border-b-2 border-red-400 text-red-300"
                : "text-gray-400 hover:text-gray-300"
            }`}
          >
            Preferences
          </button>
          <button
            onClick={() => setActiveTab("top-rated")}
            className={`px-6 py-3 text-sm font-medium transition ${
              activeTab === "top-rated"
                ? "border-b-2 border-red-400 text-red-300"
                : "text-gray-400 hover:text-gray-300"
            }`}
          >
            Top Rated ({topRated.top_movies.length + topRated.top_shows.length})
          </button>
          <button
            onClick={() => setActiveTab("recommendations")}
            className={`px-6 py-3 text-sm font-medium transition ${
              activeTab === "recommendations"
                ? "border-b-2 border-red-400 text-red-300"
                : "text-gray-400 hover:text-gray-300"
            }`}
          >
            Recommendations ({recommendations.length})
          </button>
        </div>

        {/* Content */}
        {loading ? (
          <div className="flex items-center justify-center py-16">
            <div className="h-8 w-8 animate-spin rounded-full border-3 border-red-400 border-t-transparent" />
          </div>
        ) : activeTab === "preferences" ? (
          <div className="rounded-xl bg-gradient-to-br from-[#141827]/80 to-[#0a0e1a]/60 border border-red-900/30 p-8 shadow-xl shadow-black/40 backdrop-blur-sm">
            <form onSubmit={handleSave} className="space-y-6">
              {error && (
                <div className="p-4 rounded-lg bg-red-500/10 border border-red-500/30 text-red-400 text-sm">
                  {error}
                </div>
              )}
              {success && (
                <div className="p-4 rounded-lg bg-green-500/10 border border-green-500/30 text-green-400 text-sm">
                  {success}
                </div>
              )}

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Favorite Actor
                </label>
                <input
                  type="text"
                  value={favorites.fav_actor || ""}
                  onChange={(e) => setFavorites({ ...favorites, fav_actor: e.target.value })}
                  placeholder="Enter actor name"
                  className="w-full rounded-lg border border-red-900/30 bg-[#0a0e1a]/50 px-4 py-2.5 text-sm text-white placeholder-gray-500 focus:border-red-500 focus:outline-none focus:ring-2 focus:ring-red-500/30 transition"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Favorite Genre
                </label>
                <select
                  value={favorites.fav_genre || ""}
                  onChange={(e) => setFavorites({ ...favorites, fav_genre: e.target.value ? parseInt(e.target.value) : null })}
                  className="w-full rounded-lg border border-red-900/30 bg-[#0a0e1a]/50 px-4 py-2.5 text-sm text-white focus:border-red-500 focus:outline-none focus:ring-2 focus:ring-red-500/30 transition"
                >
                  <option value="">Select a genre</option>
                  {genres.map((genre, idx) => (
                    <option key={idx} value={idx + 1}>{genre}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Favorite Decade
                </label>
                <select
                  value={favorites.fav_decade || ""}
                  onChange={(e) => setFavorites({ ...favorites, fav_decade: e.target.value })}
                  className="w-full rounded-lg border border-red-900/30 bg-[#0a0e1a]/50 px-4 py-2.5 text-sm text-white focus:border-red-500 focus:outline-none focus:ring-2 focus:ring-red-500/30 transition"
                >
                  <option value="">Select a decade</option>
                  {decades.map((decade) => (
                    <option key={decade} value={decade}>{decade}</option>
                  ))}
                </select>
              </div>

              <div className="flex gap-3 pt-4">
                <button
                  type="submit"
                  disabled={saving}
                  className="flex-1 rounded-lg bg-gradient-to-r from-red-500 to-red-600 px-6 py-3 text-sm font-medium text-white hover:from-red-600 hover:to-red-700 transition shadow-lg shadow-red-500/30 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {saving ? "Saving..." : "Save Preferences"}
                </button>
              </div>
            </form>
          </div>
        ) : activeTab === "top-rated" ? (
          <div className="space-y-6">
            {topRated.top_movies.length > 0 && (
              <div className="rounded-xl bg-gradient-to-br from-[#141827]/80 to-[#0a0e1a]/60 border border-red-900/30 p-6 shadow-xl shadow-black/40 backdrop-blur-sm">
                <h2 className="text-lg font-semibold text-white mb-4">Top Rated Movies</h2>
                <div className="space-y-3">
                  {topRated.top_movies.map((movie) => (
                    <div
                      key={movie.film_id}
                      className="rounded-lg bg-[#0a0e1a]/60 border border-red-900/30 p-4 hover:bg-red-500/10 transition"
                    >
                      <div className="flex items-start justify-between gap-4">
                        <div className="flex-1">
                          <h3 className="text-base font-semibold text-white mb-1">{movie.title}</h3>
                          <div className="flex flex-wrap items-center gap-2 text-xs text-gray-400">
                            {movie.year && <span>{movie.year}</span>}
                            {movie.genre && <span className="text-red-300">• {movie.genre}</span>}
                            <span className="text-red-400 font-semibold">{movie.rating}/10</span>
                          </div>
                          {movie.review && (
                            <p className="text-sm text-gray-300 mt-2 line-clamp-2">{movie.review}</p>
                          )}
                        </div>
                        <Link
                          href={`/reviews?film_id=${movie.film_id}`}
                          className="px-3 py-1.5 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 hover:bg-red-500/20 transition text-xs font-medium"
                        >
                          View
                        </Link>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {topRated.top_shows.length > 0 && (
              <div className="rounded-xl bg-gradient-to-br from-[#141827]/80 to-[#0a0e1a]/60 border border-red-900/30 p-6 shadow-xl shadow-black/40 backdrop-blur-sm">
                <h2 className="text-lg font-semibold text-white mb-4">Top Rated Shows</h2>
                <div className="space-y-3">
                  {topRated.top_shows.map((show) => (
                    <div
                      key={show.show_id}
                      className="rounded-lg bg-[#0a0e1a]/60 border border-red-900/30 p-4 hover:bg-red-500/10 transition"
                    >
                      <div className="flex items-start justify-between gap-4">
                        <div className="flex-1">
                          <h3 className="text-base font-semibold text-white mb-1">{show.title}</h3>
                          <div className="flex flex-wrap items-center gap-2 text-xs text-gray-400">
                            {show.years && <span>{show.years}</span>}
                            {show.genre && <span className="text-red-300">• {show.genre}</span>}
                            <span className="text-red-400 font-semibold">{show.rating}/10</span>
                          </div>
                          {show.review && (
                            <p className="text-sm text-gray-300 mt-2 line-clamp-2">{show.review}</p>
                          )}
                        </div>
                        <Link
                          href={`/reviews?show_id=${show.show_id}`}
                          className="px-3 py-1.5 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 hover:bg-red-500/20 transition text-xs font-medium"
                        >
                          View
                        </Link>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {topRated.top_movies.length === 0 && topRated.top_shows.length === 0 && (
              <div className="rounded-xl bg-gradient-to-br from-[#141827]/80 to-[#0a0e1a]/60 border border-red-900/30 p-12 text-center shadow-xl shadow-black/40 backdrop-blur-sm">
                <p className="text-gray-400 mb-4">No top-rated content yet.</p>
                <p className="text-sm text-gray-500">Start reviewing movies and shows to see your favorites here!</p>
                <Link
                  href="/reviews"
                  className="mt-4 inline-block px-4 py-2 rounded-lg bg-gradient-to-r from-red-500 to-red-600 text-white hover:from-red-600 hover:to-red-700 transition text-sm font-medium"
                >
                  Write Reviews
                </Link>
              </div>
            )}
          </div>
        ) : (
          <div className="rounded-xl bg-gradient-to-br from-[#141827]/80 to-[#0a0e1a]/60 border border-red-900/30 p-6 shadow-xl shadow-black/40 backdrop-blur-sm">
            <h2 className="text-lg font-semibold text-white mb-4">
              Personalized Recommendations
              {favorites.fav_genre_name && (
                <span className="text-sm text-gray-400 ml-2">
                  (Based on your preferences)
                </span>
              )}
            </h2>
            {recommendations.length > 0 ? (
              <div className="space-y-3">
                {recommendations.map((rec) => (
                  <div
                    key={rec.film_id}
                    className="rounded-lg bg-[#0a0e1a]/60 border border-red-900/30 p-4 hover:bg-red-500/10 transition"
                  >
                    <div className="flex items-start justify-between gap-4">
                      <div className="flex-1">
                        <h3 className="text-base font-semibold text-white mb-1">{rec.title}</h3>
                        <div className="flex flex-wrap items-center gap-2 text-xs text-gray-400">
                          {rec.year && <span>{rec.year}</span>}
                          {rec.genre && <span className="text-red-300">• {rec.genre}</span>}
                          {rec.director && <span>• Dir: {rec.director}</span>}
                          {rec.runtime > 0 && <span>• {rec.runtime} min</span>}
                          {rec.rating > 0 && (
                            <span className="text-red-400 font-semibold">{rec.rating.toFixed(1)}/10</span>
                          )}
                        </div>
                      </div>
                      <Link
                        href="/dashboard"
                        className="px-3 py-1.5 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 hover:bg-red-500/20 transition text-xs font-medium"
                      >
                        View
                      </Link>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="py-12 text-center">
                <p className="text-gray-400 mb-4">No recommendations yet.</p>
                <p className="text-sm text-gray-500 mb-4">
                  Set your preferences above to get personalized recommendations!
                </p>
                <button
                  onClick={() => setActiveTab("preferences")}
                  className="px-4 py-2 rounded-lg bg-gradient-to-r from-red-500 to-red-600 text-white hover:from-red-600 hover:to-red-700 transition text-sm font-medium"
                >
                  Set Preferences
                </button>
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
}
