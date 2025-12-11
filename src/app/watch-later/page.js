"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { api } from "@/lib/api";
import Navbar from "@/components/Navbar";

export default function WatchLaterPage() {
  const [activeTab, setActiveTab] = useState("movies");
  const [movies, setMovies] = useState([]);
  const [shows, setShows] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const router = useRouter();

  useEffect(() => {
    fetchWatchLater();
  }, [activeTab]);

  const fetchWatchLater = async () => {
    setLoading(true);
    setError("");
    try {
      const user = JSON.parse(localStorage.getItem("user") || "{}");
      if (!user.user_id) {
        router.push("/signin");
        return;
      }

      if (activeTab === "movies") {
        const response = await fetch(api.watchLaterMovie(), {
          credentials: "include",
        });
        const data = await response.json();
        if (data.success) {
          setMovies(data.movies || []);
        } else {
          setError(data.error || "Failed to fetch watch later movies");
        }
      } else {
        const response = await fetch(api.watchLaterShow(), {
          credentials: "include",
        });
        const data = await response.json();
        if (data.success) {
          setShows(data.shows || []);
        } else {
          setError(data.error || "Failed to fetch watch later shows");
        }
      }
    } catch (err) {
      setError("Network error. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const removeFromWatchLater = async (id, type) => {
    try {
      const url = type === "movie" ? api.watchLaterMovie(id) : api.watchLaterShow(id);
      const response = await fetch(url, {
        method: "DELETE",
        credentials: "include",
      });
      const data = await response.json();
      if (data.success) {
        fetchWatchLater();
      }
    } catch (err) {
      console.error("Error removing from watch later:", err);
    }
  };

  const items = activeTab === "movies" ? movies : shows;

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#0a0e1a] via-[#141827] to-[#0f1525] text-[#e8eaf6]">
      <Navbar 
        pageTitle="Watch Later"
        pageSubtitle={`Your saved ${activeTab === "movies" ? "movies" : "shows"}`}
      />

      <main className="mx-auto max-w-7xl px-6 py-8">
        <div className="mb-6 flex gap-2 border-b border-red-900/20">
          <button
            onClick={() => setActiveTab("movies")}
            className={`px-6 py-3 text-sm font-medium transition ${
              activeTab === "movies"
                ? "border-b-2 border-red-400 text-red-300"
                : "text-gray-400 hover:text-gray-300"
            }`}
          >
            Movies ({movies.length})
          </button>
          <button
            onClick={() => setActiveTab("shows")}
            className={`px-6 py-3 text-sm font-medium transition ${
              activeTab === "shows"
                ? "border-b-2 border-red-400 text-red-300"
                : "text-gray-400 hover:text-gray-300"
            }`}
          >
            TV Shows ({shows.length})
          </button>
        </div>

        <div className="rounded-xl bg-gradient-to-br from-[#141827]/80 to-[#0a0e1a]/60 border border-red-900/30 p-6 shadow-xl shadow-black/40 backdrop-blur-sm">
          {loading ? (
            <div className="flex items-center justify-center py-16">
              <div className="h-8 w-8 animate-spin rounded-full border-3 border-red-400 border-t-transparent" />
            </div>
          ) : error ? (
            <div className="py-12 text-center">
              <p className="text-sm text-red-400">{error}</p>
            </div>
          ) : items.length === 0 ? (
            <div className="py-12 text-center">
              <p className="text-sm text-gray-400">No {activeTab} in your watch later list.</p>
              <Link
                href="/dashboard"
                className="mt-4 inline-block px-4 py-2 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 hover:bg-red-500/20 transition text-sm font-medium"
              >
                Browse {activeTab === "movies" ? "Movies" : "Shows"}
              </Link>
            </div>
          ) : (
            <div className="space-y-3">
              {items.map((item) => (
                <div
                  key={item.film_id || item.show_id}
                  className="group rounded-lg bg-[#0a0e1a]/60 border border-red-900/30 px-5 py-5 transition hover:bg-red-500/10 hover:border-red-500/40 hover:shadow-lg hover:shadow-red-500/10"
                >
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1">
                      <h3 className="text-lg font-semibold text-white mb-2 group-hover:text-red-300 transition">
                        {item.title}
                      </h3>
                      <div className="flex flex-wrap items-center gap-3 text-xs text-gray-400">
                        {item.year && <span className="px-2 py-1 rounded bg-red-500/10 text-red-300">{item.year}</span>}
                        {item.years && <span className="px-2 py-1 rounded bg-red-500/10 text-red-300">{item.years}</span>}
                        {item.runtime > 0 && <span>{item.runtime} min</span>}
                        {item.genre && <span className="text-red-300 font-medium">{item.genre}</span>}
                        {item.director && <span className="text-gray-300">Dir: {item.director}</span>}
                        {item.rating && <span className="px-2 py-1 rounded bg-red-500/10 text-red-300">{item.rating}</span>}
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Link
                        href={`/reviews?${activeTab === "movies" ? 'film_id' : 'show_id'}=${item.film_id || item.show_id}`}
                        className="px-3 py-2 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 hover:bg-red-500/20 transition text-xs font-medium"
                      >
                        Review
                      </Link>
                      <button
                        onClick={() => removeFromWatchLater(item.film_id || item.show_id, activeTab === "movies" ? "movie" : "show")}
                        className="px-4 py-2 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 hover:bg-red-500/20 transition text-sm font-medium whitespace-nowrap"
                      >
                        Remove
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </main>
    </div>
  );
}

