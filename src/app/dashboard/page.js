"use client";

import { useMemo, useState, useEffect } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import Navbar from "@/components/Navbar";

function Pill({ label, active, onClick, variant = "default" }) {
  if (variant === "chip") {
    return (
      <button
        onClick={onClick}
        className={`rounded-full px-4 py-2 text-sm font-medium transition ${
          active
            ? "bg-red-500/20 text-red-300 border border-red-500/30"
            : "bg-[#0a0e1a]/50 text-gray-400 hover:bg-red-500/10 hover:text-red-300 border border-red-900/30"
        }`}
      >
        {label}
      </button>
    );
  }
  
  return (
    <button
      onClick={onClick}
      className={`rounded-lg px-4 py-2.5 text-sm font-medium transition ${
        active
          ? "bg-red-500/20 text-red-300 border border-red-500/30"
            : "bg-[#0a0e1a]/50 text-gray-400 hover:bg-red-500/10 hover:text-red-300 border border-red-900/30"
      }`}
    >
      {label}
    </button>
  );
}

export default function DashboardPage() {
  const [activeTab, setActiveTab] = useState("movies"); // "movies" or "shows"
  const [genre, setGenre] = useState("");
  const [maxRating, setMaxRating] = useState("R");
  const [yearRange, setYearRange] = useState([1900, 2024]);
  const [minRating, setMinRating] = useState(0);
  const [minVotes, setMinVotes] = useState(0);
  const [sortBy, setSortBy] = useState("rating");
  const [titleSearch, setTitleSearch] = useState("");
  const [showAdvanced, setShowAdvanced] = useState(false);
  
  const [movies, setMovies] = useState([]);
  const [genreOptions, setGenreOptions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [genresLoaded, setGenresLoaded] = useState(false);
  const [user, setUser] = useState(null);
  const [watchLaterMovies, setWatchLaterMovies] = useState(new Set());
  const [watchLaterShows, setWatchLaterShows] = useState(new Set());
  const router = useRouter();

  // Fetch genres based on active tab
  useEffect(() => {
    const fetchGenres = async () => {
      try {
        setGenresLoaded(false);
        const endpoint = activeTab === "movies" ? api.genres : api.showGenres;
        const response = await fetch(endpoint);
        const data = await response.json();
        
        if (data.success) {
          setGenreOptions(data.genres || []);
          setGenresLoaded(true);
        } else {
          setGenresLoaded(true);
        }
      } catch (err) {
        console.error("Error fetching genres:", err);
        setGenresLoaded(true);
      }
    };

    fetchGenres();
  }, [activeTab]);

  // Check user authentication
  useEffect(() => {
    const userData = localStorage.getItem("user");
    if (userData) {
      setUser(JSON.parse(userData));
    }
  }, []);

  // Fetch watch later lists
  useEffect(() => {
    if (user?.user_id) {
      fetchWatchLater();
    }
  }, [user]);

  const fetchWatchLater = async () => {
    try {
      const [moviesRes, showsRes] = await Promise.all([
        fetch(api.watchLaterMovie(), { credentials: "include" }),
        fetch(api.watchLaterShow(), { credentials: "include" }),
      ]);
      const moviesData = await moviesRes.json();
      const showsData = await showsRes.json();
      if (moviesData.success) {
        setWatchLaterMovies(new Set(moviesData.movies?.map(m => m.film_id) || []));
      }
      if (showsData.success) {
        setWatchLaterShows(new Set(showsData.shows?.map(s => s.show_id) || []));
      }
    } catch (err) {
      console.error("Error fetching watch later:", err);
    }
  };

  const toggleWatchLater = async (id, type) => {
    if (!user?.user_id) {
      router.push("/signin");
      return;
    }

    const isInList = type === "movie" 
      ? watchLaterMovies.has(id) 
      : watchLaterShows.has(id);
    
    try {
      const url = type === "movie" 
        ? api.watchLaterMovie(id) 
        : api.watchLaterShow(id);
      
      const response = await fetch(url, {
        method: isInList ? "DELETE" : "POST",
        credentials: "include",
      });
      
      const data = await response.json();
      if (data.success) {
        if (type === "movie") {
          const newSet = new Set(watchLaterMovies);
          if (isInList) {
            newSet.delete(id);
          } else {
            newSet.add(id);
          }
          setWatchLaterMovies(newSet);
        } else {
          const newSet = new Set(watchLaterShows);
          if (isInList) {
            newSet.delete(id);
          } else {
            newSet.add(id);
          }
          setWatchLaterShows(newSet);
        }
      }
    } catch (err) {
      console.error("Error toggling watch later:", err);
    }
  };

  // Fetch movies or shows based on active tab
  useEffect(() => {
    const fetchData = async () => {
      if (!genresLoaded) return;
      
      setLoading(true);
      setError(null);

      try {
        const params = new URLSearchParams();
        if (genre && genre !== "") params.append("genre", genre);
        if (maxRating) params.append("maxRating", maxRating);
        params.append("yearFrom", yearRange[0]);
        params.append("yearTo", yearRange[1]);
        if (minRating > 0) params.append("minRating", minRating);
        if (minVotes > 0) params.append("minVotes", minVotes);
        if (titleSearch) params.append("titleSearch", titleSearch);
        params.append("sortBy", sortBy);
        params.append("limit", "100");

        const endpoint = activeTab === "movies" ? api.movies : api.shows;
        const response = await fetch(`${endpoint}?${params.toString()}`);
        const data = await response.json();

        if (data.success) {
          setMovies(data.movies || []);
          if (data.movies && data.movies.length === 0) {
            setError(`No ${activeTab} found matching your criteria.`);
          }
        } else {
          setError(data.error || `Failed to fetch ${activeTab}`);
        }
      } catch (err) {
        console.error(`Error fetching ${activeTab}:`, err);
        setError(`Failed to load ${activeTab}: ${err.message}`);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [activeTab, genre, maxRating, yearRange, minRating, minVotes, sortBy, titleSearch, genresLoaded]);

  const recommendation = useMemo(() => {
    if (movies.length === 0) return null;
    
    const sorted = [...movies].sort((a, b) => {
      if (b.score !== a.score) {
        return b.score - a.score;
      }
      return b.rating_value - a.rating_value;
    });

    return sorted[0];
  }, [movies]);

  const primaryGenres = useMemo(() => genreOptions.slice(0, 8), [genreOptions]);
  const sortLabel = useMemo(() => {
    const labels = {
      rating: "Rating",
      votes: "Votes",
      year: "Newest first",
      year_old: "Oldest first",
      runtime: "Shortest runtime",
      runtime_long: "Longest runtime"
    };
    return labels[sortBy] || "Rating";
  }, [sortBy]);

  const clearAllFilters = () => {
    setGenre("");
    setYearRange([1900, 2024]);
    setMinRating(0);
    setMinVotes(0);
    setTitleSearch("");
    setSortBy("rating");
    setMaxRating("R");
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#0a0e1a] via-[#141827] to-[#0f1525] text-[#e8eaf6]">
      <Navbar 
        pageTitle="WhatToWatch"
        pageSubtitle={`Discover your next favorite ${activeTab === "movies" ? "film" : "show"}`}
        showStats={true}
        statsCount={movies.length}
      />

      <main className="mx-auto max-w-7xl px-6 py-8">
        {/* Tab Navigation */}
        <div className="mb-6 flex gap-2 border-b border-red-900/20">
          <button
            onClick={() => {
              setActiveTab("movies");
              setGenre(""); // Reset genre when switching tabs
            }}
            className={`px-6 py-3 text-sm font-medium transition ${
              activeTab === "movies"
                ? "border-b-2 border-red-400 text-red-300"
                : "text-gray-400 hover:text-gray-300"
            }`}
          >
            Movies
          </button>
          <button
            onClick={() => {
              setActiveTab("shows");
              setGenre(""); // Reset genre when switching tabs
            }}
            className={`px-6 py-3 text-sm font-medium transition ${
              activeTab === "shows"
                ? "border-b-2 border-red-400 text-red-300"
                : "text-gray-400 hover:text-gray-300"
            }`}
          >
            TV Shows
          </button>
        </div>

        <div className="flex flex-col gap-6 lg:flex-row">
          {/* Left Sidebar - Filters */}
          <aside className="w-full flex-shrink-0 space-y-4 lg:w-80">
            <section className="rounded-xl bg-gradient-to-br from-[#141827]/80 to-[#0a0e1a]/60 border border-red-900/30 p-6 space-y-5 backdrop-blur-sm shadow-xl shadow-black/40">
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-lg font-semibold text-white">Filters</h3>
                <button
                  onClick={clearAllFilters}
                  className="text-sm text-gray-400 hover:text-red-400 transition font-medium px-2 py-1 rounded hover:bg-red-500/10"
                >
                  Reset All
                </button>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">Search Title</label>
                <input
                  type="text"
                  placeholder={`Enter ${activeTab === "movies" ? "movie" : "show"} title...`}
                  value={titleSearch}
                  onChange={(e) => setTitleSearch(e.target.value)}
                  className="w-full rounded-lg border border-red-900/30 bg-[#0a0e1a]/50 px-4 py-2.5 text-sm text-white placeholder-gray-500 focus:border-red-500 focus:outline-none focus:ring-2 focus:ring-red-500/30 transition"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-3">Genre</label>
                <div className="flex flex-wrap gap-2">
                  <Pill label="Any" active={!genre} onClick={() => setGenre("")} />
                  {primaryGenres.map((option) => (
                    <Pill
                      key={option}
                      label={option}
                      active={genre === option}
                      onClick={() => setGenre(option)}
                    />
                  ))}
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">Max Rating</label>
                <select
                  value={maxRating}
                  onChange={(e) => setMaxRating(e.target.value)}
                  className="w-full rounded-lg border border-red-900/30 bg-[#0a0e1a]/50 px-4 py-2.5 text-sm text-white focus:border-red-500 focus:outline-none focus:ring-2 focus:ring-red-500/30 transition"
                >
                  <option value="G">Up to G</option>
                  <option value="PG">Up to PG</option>
                  <option value="PG-13">Up to PG-13</option>
                  <option value="R">Up to R</option>
                  <option value="NC-17">Up to NC-17</option>
                  {activeTab === "shows" && (
                    <>
                      <option value="TV-G">Up to TV-G</option>
                      <option value="TV-PG">Up to TV-PG</option>
                      <option value="TV-14">Up to TV-14</option>
                      <option value="TV-MA">Up to TV-MA</option>
                    </>
                  )}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-3">Year</label>
                <div className="flex flex-wrap gap-2">
                  {["2020s", "2010s", "2000s", "1990s"].map((decade) => {
                    const [start, end] =
                      decade === "2020s"
                        ? [2020, 2024]
                        : decade === "2010s"
                        ? [2010, 2019]
                        : decade === "2000s"
                        ? [2000, 2009]
                        : [1990, 1999];
                    const active = yearRange[0] === start && yearRange[1] === end;
                    return (
                      <button
                        key={decade}
                        onClick={() => setYearRange([start, end])}
                        className={`rounded-lg px-4 py-2 text-sm font-medium transition ${
                          active 
                            ? "bg-red-500/20 text-red-300 border border-red-500/30" 
                            : "bg-[#0a0e1a]/50 text-gray-400 hover:bg-red-500/10 border border-red-900/30"
                        }`}
                      >
                        {decade}
                      </button>
                    );
                  })}
                </div>
              </div>
            </section>

            <section className="rounded-xl bg-gradient-to-br from-[#141827]/80 to-[#0a0e1a]/60 border border-red-900/30 overflow-hidden backdrop-blur-sm shadow-xl shadow-black/40">
              <button
                className="flex w-full items-center justify-between px-6 py-4 text-base font-medium text-white hover:bg-red-500/10 transition border-b border-red-900/20"
                onClick={() => setShowAdvanced((prev) => !prev)}
              >
                <span className="font-semibold">Advanced Filters</span>
                <span className="text-lg text-gray-400 font-bold">{showAdvanced ? "−" : "+"}</span>
              </button>
              {showAdvanced && (
                <div className="space-y-5 border-t border-red-900/20 px-6 py-5">
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <label className="block text-sm font-medium text-gray-300">Min Rating</label>
                      <span className="text-sm text-gray-400">{minRating > 0 ? minRating.toFixed(1) : "Any"}</span>
                    </div>
                    <input
                      type="range"
                      min="0"
                      max="10"
                      step="0.5"
                      value={minRating}
                      onChange={(e) => setMinRating(Number(e.target.value))}
                      className="h-2 w-full cursor-pointer appearance-none rounded-full bg-[#0a0e1a] accent-red-500"
                    />
                  </div>

                  {activeTab === "movies" && (
                    <div>
                      <div className="flex items-center justify-between mb-2">
                        <label className="block text-sm font-medium text-gray-300">Min Votes</label>
                        <span className="text-sm text-gray-400">{minVotes > 0 ? `${(minVotes / 1000).toFixed(0)}k` : "Any"}</span>
                      </div>
                      <input
                        type="range"
                        min="0"
                        max="1000000"
                        step="10000"
                        value={minVotes}
                        onChange={(e) => setMinVotes(Number(e.target.value))}
                        className="h-2 w-full cursor-pointer appearance-none rounded-full bg-[#0a0e1a] accent-red-500"
                      />
                    </div>
                  )}

                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">Sort By</label>
                    <select
                      value={sortBy}
                      onChange={(e) => setSortBy(e.target.value)}
                      className="w-full rounded-lg border border-red-900/30 bg-[#0a0e1a]/50 px-4 py-2.5 text-sm text-white focus:border-red-500 focus:outline-none focus:ring-2 focus:ring-red-500/30 transition"
                    >
                      <option value="rating">Rating (High to Low)</option>
                      {activeTab === "movies" && <option value="votes">Votes (Most Popular)</option>}
                      <option value="year">Year (Newest First)</option>
                      <option value="year_old">Year (Oldest First)</option>
                      <option value="runtime">Runtime (Shortest First)</option>
                      <option value="runtime_long">Runtime (Longest First)</option>
                    </select>
                  </div>
                </div>
              )}
            </section>
          </aside>

          {/* Right Side - Content */}
          <div className="flex-1 space-y-6 min-w-0">
            {/* Top Recommendation */}
            {recommendation ? (
              <article className="rounded-xl bg-gradient-to-br from-[#141827]/80 to-[#0a0e1a]/80 border border-red-900/30 p-6 shadow-2xl shadow-black/50 backdrop-blur-sm">
                <div className="flex items-start justify-between gap-4 mb-4">
                  <div className="flex-1">
                    <div className="flex flex-wrap items-center gap-2 text-sm text-gray-400 mb-3">
                      {recommendation.year && <span>{recommendation.year}</span>}
                      {recommendation.rating_value > 0 && (
                        <>
                          <span>•</span>
                            <span className="text-red-400 font-semibold">{recommendation.rating_value.toFixed(1)}/10</span>
                        </>
                      )}
                      {recommendation.runtime > 0 && (
                        <>
                          <span>•</span>
                          <span>{recommendation.runtime} min</span>
                        </>
                      )}
                    </div>
                    <h2 className="text-2xl font-bold text-white mb-3">{recommendation.title}</h2>
                    <p className="text-sm leading-relaxed text-gray-300 mb-4">{recommendation.synopsis}</p>
                    <div className="flex flex-wrap gap-2 mb-4">
                      {recommendation.genres?.slice(0, 4).map((g) => (
                        <span key={g} className="rounded-full bg-red-500/20 px-3 py-1.5 text-xs font-medium text-red-300 border border-red-500/30">
                          {g}
                        </span>
                      ))}
                      {recommendation.rating && recommendation.rating !== "Unrated" && (
                        <span className="rounded-full bg-red-500/10 px-3 py-1.5 text-xs font-medium text-gray-300 border border-red-900/30">
                          {recommendation.rating}
                        </span>
                      )}
                    </div>
                    {recommendation.cast && recommendation.cast.length > 0 && (
                      <p className="text-sm text-gray-400 mb-4">
                        <span className="text-gray-500">Cast: </span>
                        {Array.isArray(recommendation.cast)
                          ? recommendation.cast.filter(Boolean).slice(0, 5).join(", ")
                          : ""}
                      </p>
                    )}
                  </div>
                </div>
                {user?.user_id && (
                  <div className="flex items-center gap-3 pt-4 border-t border-red-900/20">
                    <button
                      onClick={() => {
                        const id = recommendation.film_id || recommendation.show_id;
                        toggleWatchLater(id, activeTab === "movies" ? "movie" : "show");
                      }}
                      className={`px-4 py-2 rounded-lg text-sm font-medium transition ${
                        (recommendation.film_id && watchLaterMovies.has(recommendation.film_id)) ||
                        (recommendation.show_id && watchLaterShows.has(recommendation.show_id))
                          ? "bg-red-500/20 text-red-300 border border-red-500/30"
                          : "bg-red-500/10 text-red-400 border border-red-500/20 hover:bg-red-500/20"
                      }`}
                    >
                      {(recommendation.film_id && watchLaterMovies.has(recommendation.film_id)) ||
                      (recommendation.show_id && watchLaterShows.has(recommendation.show_id))
                        ? "In Watch Later"
                        : "+ Add to Watch Later"}
                    </button>
                    <Link
                      href={`/reviews?${activeTab === "movies" ? 'film_id' : 'show_id'}=${recommendation.film_id || recommendation.show_id}`}
                      className="px-4 py-2 rounded-lg bg-red-500/10 text-red-400 border border-red-500/20 hover:bg-red-500/20 transition text-sm font-medium"
                    >
                      Write Review
                    </Link>
                  </div>
                )}
              </article>
            ) : (
              <article className="rounded-xl bg-[#141827]/60 border border-red-900/20 p-12 text-center shadow-xl shadow-black/30 backdrop-blur-sm">
                <p className="text-gray-400">Adjust filters to see recommendations</p>
                <p className="text-xs text-gray-500 mt-2">Use the filters on the left to find your next watch</p>
              </article>
            )}

            {/* Movie/Show List */}
            <section className="rounded-xl bg-gradient-to-br from-[#141827]/80 to-[#0a0e1a]/60 border border-red-900/30 p-6 shadow-xl shadow-black/40 backdrop-blur-sm">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-lg font-semibold text-white">
                  {movies.length} {movies.length === 1 ? "match" : "matches"} found
                </h3>
                <div className="flex items-center gap-2">
                  <span className="text-xs text-gray-500">Sort:</span>
                  <span className="text-sm font-medium text-red-400">{sortLabel}</span>
                </div>
              </div>

              {loading ? (
                <div className="flex items-center justify-center py-16">
                  <div className="h-8 w-8 animate-spin rounded-full border-3 border-red-400 border-t-transparent" />
                </div>
              ) : error ? (
                <div className="py-12 text-center">
                  <p className="text-sm text-red-400">{error}</p>
                </div>
              ) : movies.length === 0 ? (
                <div className="py-12 text-center">
                  <p className="text-sm text-gray-400">No {activeTab} found. Try adjusting your filters.</p>
                </div>
              ) : (
                <div className="space-y-3 max-h-[600px] overflow-y-auto">
                  {movies.map((movie, index) => {
                    const movieId = movie.film_id || movie.show_id;
                    const isMovie = activeTab === "movies";
                    const isInWatchLater = isMovie 
                      ? watchLaterMovies.has(movieId)
                      : watchLaterShows.has(movieId);
                    
                    return (
                      <div
                        key={movie.title + index}
                        className="group rounded-lg bg-[#0a0e1a]/50 border border-red-900/20 px-4 py-4 transition hover:bg-red-500/10 hover:border-red-500/30"
                      >
                        <div className="flex items-start justify-between gap-4">
                          <button
                            className="flex-1 text-left"
                            onClick={() => {
                              window.scrollTo({ top: 0, behavior: "smooth" });
                              const next = [...movies];
                              [next[0], next[index]] = [next[index], next[0]];
                              setMovies(next);
                            }}
                          >
                            <div className="flex items-center gap-2 mb-1">
                              <span className="text-sm font-semibold text-white group-hover:text-red-300 transition">
                                {movie.title}
                              </span>
                              {movie.rating_value > 0 && (
                                <>
                                  <span className="text-gray-600">•</span>
                                  <span className="text-sm text-red-400">{movie.rating_value.toFixed(1)}/10</span>
                                </>
                              )}
                            </div>
                            <div className="flex flex-wrap items-center gap-2 text-xs text-gray-400">
                              {movie.genres?.slice(0, 2).map((g) => (
                                <span key={g} className="text-red-300">{g}</span>
                              ))}
                              {movie.year && <span>• {movie.year}</span>}
                              {movie.runtime > 0 && <span>• {movie.runtime} min</span>}
                              {movie.rating && movie.rating !== "Unrated" && <span>• {movie.rating}</span>}
                            </div>
                          </button>
                          <div className="flex items-center gap-2">
                            {user?.user_id && (
                              <>
                                <button
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    toggleWatchLater(movieId, isMovie ? "movie" : "show");
                                  }}
                                  className={`px-3 py-1.5 rounded text-xs font-medium transition ${
                                    isInWatchLater
                                      ? "bg-red-500/20 text-red-300 border border-red-500/30"
                                      : "bg-[#141827]/50 text-gray-400 border border-red-900/30 hover:bg-red-500/10 hover:text-red-300"
                                  }`}
                                  title={isInWatchLater ? "Remove from watch later" : "Add to watch later"}
                                >
                                  {isInWatchLater ? "Saved" : "Watch Later"}
                                </button>
                                <Link
                                  href={`/reviews?${isMovie ? 'film_id' : 'show_id'}=${movieId}`}
                                  onClick={(e) => e.stopPropagation()}
                                  className="px-3 py-1.5 rounded text-xs font-medium bg-[#141827]/50 text-gray-400 border border-red-900/30 hover:bg-red-500/10 hover:text-red-300 transition"
                                >
                                  Review
                                </Link>
                              </>
                            )}
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </section>
          </div>
        </div>
      </main>
    </div>
  );
}
