"use client";

import { useMemo, useState, useEffect } from "react";

function Pill({ label, active, onClick, variant = "default" }) {
  if (variant === "chip") {
    return (
      <button
        onClick={onClick}
        className={`rounded-full px-4 py-2 text-sm font-medium transition ${
          active
            ? "bg-cyan-500/20 text-cyan-300 border border-cyan-500/30"
            : "bg-slate-800/50 text-slate-400 hover:bg-slate-700/50 hover:text-slate-300 border border-slate-700/50"
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
          ? "bg-cyan-500/20 text-cyan-300 border border-cyan-500/30"
          : "bg-slate-800/50 text-slate-400 hover:bg-slate-700/50 hover:text-slate-300 border border-slate-700/50"
      }`}
    >
      {label}
    </button>
  );
}

export default function DashboardPage() {
  const [genre, setGenre] = useState("");
  const [runtime, setRuntime] = useState(115);
  const [maxRating, setMaxRating] = useState("R");
  const [selectedActors, setSelectedActors] = useState([]);
  const [yearRange, setYearRange] = useState([1900, 2024]);
  const [minRating, setMinRating] = useState(0);
  const [minVotes, setMinVotes] = useState(0);
  const [sortBy, setSortBy] = useState("rating");
  const [titleSearch, setTitleSearch] = useState("");
  const [showAdvanced, setShowAdvanced] = useState(false);
  
  const [movies, setMovies] = useState([]);
  const [genreOptions, setGenreOptions] = useState([]);
  const [actorOptions, setActorOptions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [genresLoaded, setGenresLoaded] = useState(false);

  useEffect(() => {
    const fetchInitialData = async () => {
      try {
        setLoading(true);
        const [genresRes, actorsRes] = await Promise.all([
          fetch("/api/genres"),
          fetch("/api/actors")
        ]);

        const genresData = await genresRes.json();
        const actorsData = await actorsRes.json();

        if (genresData.success) {
          setGenreOptions(genresData.genres || []);
          setGenresLoaded(true);
        } else {
          setGenresLoaded(true);
        }

        if (actorsData.success) {
          setActorOptions(actorsData.actors || []);
        }
      } catch (err) {
        console.error("Error fetching initial data:", err);
        setError("Failed to load data: " + err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchInitialData();
  }, []);

  useEffect(() => {
    const fetchMovies = async () => {
      if (!genresLoaded) return;
      
      setLoading(true);
      setError(null);

      try {
        const params = new URLSearchParams();
        if (genre && genre !== "") params.append("genre", genre);
        if (maxRating) params.append("maxRating", maxRating);
        params.append("maxRuntime", runtime);
        params.append("yearFrom", yearRange[0]);
        params.append("yearTo", yearRange[1]);
        if (minRating > 0) params.append("minRating", minRating);
        if (minVotes > 0) params.append("minVotes", minVotes);
        if (selectedActors.length > 0) params.append("actors", selectedActors.join(","));
        if (titleSearch) params.append("titleSearch", titleSearch);
        params.append("sortBy", sortBy);
        params.append("limit", "100");

        const response = await fetch(`/api/movies?${params.toString()}`);
        const data = await response.json();

        if (data.success) {
          setMovies(data.movies || []);
          if (data.movies && data.movies.length === 0) {
            setError("No movies found matching your criteria.");
          }
        } else {
          setError(data.error || "Failed to fetch movies");
        }
      } catch (err) {
        console.error("Error fetching movies:", err);
        setError(`Failed to load movies: ${err.message}`);
      } finally {
        setLoading(false);
      }
    };

    fetchMovies();
  }, [genre, maxRating, runtime, yearRange, minRating, minVotes, selectedActors, sortBy, titleSearch, genresLoaded]);

  const recommendation = useMemo(() => {
    if (movies.length === 0) return null;
    
    const sorted = [...movies].sort((a, b) => {
      if (b.score !== a.score) {
        return b.score - a.score;
      }
      const aRuntimeDiff = Math.abs(a.runtime - runtime);
      const bRuntimeDiff = Math.abs(b.runtime - runtime);
      return aRuntimeDiff - bRuntimeDiff;
    });

    return sorted[0];
  }, [movies, runtime]);

  const primaryGenres = useMemo(() => genreOptions.slice(0, 8), [genreOptions]);
  const topActors = useMemo(() => actorOptions.slice(0, 50), [actorOptions]);
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

  const toggleActor = (actorName) => {
    setSelectedActors(prev =>
      prev.includes(actorName)
        ? prev.filter(a => a !== actorName)
        : [...prev, actorName]
    );
  };

  const clearAllFilters = () => {
    setGenre("");
    setSelectedActors([]);
    setYearRange([1900, 2024]);
    setMinRating(0);
    setMinVotes(0);
    setTitleSearch("");
    setSortBy("rating");
    setRuntime(115);
    setMaxRating("R");
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <header className="border-b border-slate-800/80 bg-slate-950/95 backdrop-blur-md sticky top-0 z-50 shadow-lg shadow-black/20">
        <div className="mx-auto max-w-7xl px-6 py-5">
          <div className="flex items-center gap-4">
            <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-cyan-400 via-cyan-500 to-indigo-500 text-slate-950 font-bold text-xl shadow-lg shadow-cyan-500/30">
            W
          </div>
            <div className="flex-1">
              <h1 className="text-xl font-bold text-white tracking-tight">WhatToWatch</h1>
              <p className="text-xs text-slate-400 mt-0.5">Discover your next favorite film</p>
            </div>
            {movies.length > 0 && (
              <div className="hidden sm:flex items-center gap-2 px-4 py-2 rounded-lg bg-slate-900/60 border border-slate-800/50">
                <span className="text-sm font-medium text-cyan-400">{movies.length}</span>
                <span className="text-xs text-slate-400">{movies.length === 1 ? 'match' : 'matches'}</span>
              </div>
            )}
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-7xl px-6 py-8">
        <div className="flex flex-col gap-6 lg:flex-row">
          {/* Left Sidebar - Filters */}
          <aside className="w-full flex-shrink-0 space-y-4 lg:w-80">
            <section className="rounded-xl bg-slate-900/60 border border-slate-800/50 p-6 space-y-5">
              <div className="flex items-center justify-between">
                <h3 className="text-base font-semibold text-white">Filters</h3>
                <button
                  onClick={clearAllFilters}
                  className="text-sm text-slate-400 hover:text-slate-300 transition font-medium"
                >
                  Reset
                </button>
            </div>

              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Search Title</label>
                <input
                  type="text"
                  placeholder="Enter movie title..."
                  value={titleSearch}
                  onChange={(e) => setTitleSearch(e.target.value)}
                  className="w-full rounded-lg border border-slate-700 bg-slate-950/60 px-4 py-2.5 text-sm text-white placeholder-slate-500 focus:border-cyan-400 focus:outline-none focus:ring-2 focus:ring-cyan-400/20 transition"
                />
                  </div>

              <div>
                <label className="block text-sm font-medium text-slate-300 mb-3">Genre</label>
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

              <div className="grid gap-4 sm:grid-cols-2">
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">Max Rating</label>
                  <select
                    value={maxRating}
                    onChange={(e) => setMaxRating(e.target.value)}
                    className="w-full rounded-lg border border-slate-700 bg-slate-950/60 px-4 py-2.5 text-sm text-white focus:border-cyan-400 focus:outline-none focus:ring-2 focus:ring-cyan-400/20 transition"
                  >
                    <option value="G">Up to G</option>
                    <option value="PG">Up to PG</option>
                    <option value="PG-13">Up to PG-13</option>
                    <option value="R">Up to R</option>
                    <option value="NC-17">Up to NC-17</option>
                  </select>
                </div>
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <label className="block text-sm font-medium text-slate-300">Max Runtime</label>
                    <span className="text-sm font-medium text-cyan-400">{runtime} min</span>
                  </div>
                  <input
                    type="range"
                    min="60"
                    max="200"
                    step="5"
                    value={runtime}
                    onChange={(e) => setRuntime(Number(e.target.value))}
                    className="h-2 w-full cursor-pointer appearance-none rounded-full bg-slate-800 accent-cyan-400"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-300 mb-3">Year</label>
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
                            ? "bg-cyan-500/20 text-cyan-300 border border-cyan-500/30" 
                            : "bg-slate-800/50 text-slate-400 hover:bg-slate-700/50 border border-slate-700/50"
                        }`}
                      >
                        {decade}
                      </button>
                    );
                  })}
                </div>
              </div>
            </section>

            <section className="rounded-xl bg-slate-900/60 border border-slate-800/50 overflow-hidden">
              <button
                className="flex w-full items-center justify-between px-6 py-4 text-base font-medium text-white hover:bg-slate-800/50 transition"
                onClick={() => setShowAdvanced((prev) => !prev)}
              >
                <span>Advanced Filters</span>
                <span className="text-sm text-slate-400">{showAdvanced ? "−" : "+"}</span>
              </button>
              {showAdvanced && (
                <div className="space-y-5 border-t border-slate-800/60 px-6 py-5">
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <label className="block text-sm font-medium text-slate-300">Min Rating</label>
                      <span className="text-sm text-slate-400">{minRating > 0 ? minRating.toFixed(1) : "Any"}</span>
                    </div>
                    <input
                      type="range"
                      min="0"
                      max="10"
                      step="0.5"
                      value={minRating}
                      onChange={(e) => setMinRating(Number(e.target.value))}
                      className="h-2 w-full cursor-pointer appearance-none rounded-full bg-slate-800 accent-cyan-400"
                    />
                </div>

                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <label className="block text-sm font-medium text-slate-300">Min Votes</label>
                      <span className="text-sm text-slate-400">{minVotes > 0 ? `${(minVotes / 1000).toFixed(0)}k` : "Any"}</span>
              </div>
                    <input
                      type="range"
                      min="0"
                      max="1000000"
                      step="10000"
                      value={minVotes}
                      onChange={(e) => setMinVotes(Number(e.target.value))}
                      className="h-2 w-full cursor-pointer appearance-none rounded-full bg-slate-800 accent-cyan-400"
                    />
            </div>

                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">Sort By</label>
                    <select
                      value={sortBy}
                      onChange={(e) => setSortBy(e.target.value)}
                      className="w-full rounded-lg border border-slate-700 bg-slate-950/60 px-4 py-2.5 text-sm text-white focus:border-cyan-400 focus:outline-none focus:ring-2 focus:ring-cyan-400/20 transition"
                    >
                      <option value="rating">Rating (High to Low)</option>
                      <option value="votes">Votes (Most Popular)</option>
                      <option value="year">Year (Newest First)</option>
                      <option value="year_old">Year (Oldest First)</option>
                      <option value="runtime">Runtime (Shortest First)</option>
                      <option value="runtime_long">Runtime (Longest First)</option>
                    </select>
        </div>

                <div>
                    <div className="flex items-center justify-between mb-3">
                      <label className="block text-sm font-medium text-slate-300">Actors</label>
                      {selectedActors.length > 0 && (
                        <button
                          onClick={() => setSelectedActors([])}
                          className="text-xs text-cyan-400 hover:text-cyan-300 transition"
                        >
                          Clear ({selectedActors.length})
                        </button>
                      )}
                    </div>
                    <div className="flex max-h-48 flex-wrap gap-2 overflow-y-auto pr-1">
                      {topActors.length === 0 ? (
                        <span className="text-sm text-slate-500">Loading actors…</span>
                      ) : (
                        topActors.map((actor) => (
                          <Pill
                            key={actor}
                            label={actor}
                            active={selectedActors.includes(actor)}
                            onClick={() => toggleActor(actor)}
                            variant="chip"
                          />
                        ))
                      )}
                </div>
                  </div>
                </div>
              )}
            </section>
          </aside>

          {/* Right Side - Content */}
          <div className="flex-1 space-y-6 min-w-0">
            {/* Top Recommendation */}
            {recommendation ? (
              <article className="rounded-xl bg-slate-900/60 border border-slate-800/50 p-6 shadow-lg">
                <div className="flex flex-wrap items-center gap-2 text-sm text-slate-400 mb-3">
                  {recommendation.year && <span>{recommendation.year}</span>}
                  {recommendation.rating_value > 0 && (
                    <>
                      <span>•</span>
                      <span className="text-cyan-400">⭐ {recommendation.rating_value.toFixed(1)}</span>
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
                <p className="text-sm leading-relaxed text-slate-300 mb-4">{recommendation.synopsis}</p>
                <div className="flex flex-wrap gap-2 mb-4">
                  {recommendation.genres?.slice(0, 4).map((g) => (
                    <span key={g} className="rounded-full bg-cyan-500/20 px-3 py-1.5 text-xs font-medium text-cyan-300 border border-cyan-500/30">
                    {g}
                  </span>
                ))}
                  {recommendation.rating && recommendation.rating !== "Unrated" && (
                    <span className="rounded-full bg-slate-800/70 px-3 py-1.5 text-xs font-medium text-slate-200 border border-slate-700/50">
                  {recommendation.rating}
                </span>
                  )}
                </div>
                {recommendation.cast && recommendation.cast.length > 0 && (
                  <p className="text-sm text-slate-400">
                    <span className="text-slate-500">Cast: </span>
                    {Array.isArray(recommendation.cast)
                      ? recommendation.cast.filter(Boolean).slice(0, 5).join(", ")
                      : ""}
                  </p>
                )}
              </article>
            ) : (
              <article className="rounded-xl bg-slate-900/60 border border-slate-800/50 p-12 text-center">
                <p className="text-slate-400">Adjust filters to see recommendations</p>
              </article>
            )}

            {/* Movie List */}
            <section className="rounded-xl bg-slate-900/60 border border-slate-800/50 p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-base font-semibold text-white">
                  {movies.length} {movies.length === 1 ? "match" : "matches"}
                </h3>
                <span className="text-sm text-slate-400">Sort: {sortLabel}</span>
              </div>

              {loading ? (
                <div className="flex items-center justify-center py-16">
                  <div className="h-8 w-8 animate-spin rounded-full border-3 border-cyan-400 border-t-transparent" />
              </div>
              ) : error ? (
                <div className="py-12 text-center">
                  <p className="text-sm text-red-400">{error}</p>
            </div>
              ) : movies.length === 0 ? (
                <div className="py-12 text-center">
                  <p className="text-sm text-slate-400">No movies found. Try adjusting your filters.</p>
                </div>
              ) : (
                <div className="space-y-2 max-h-[600px] overflow-y-auto">
                  {movies.map((movie, index) => (
                    <button
                      key={movie.title + index}
                      className="w-full rounded-lg bg-slate-900/50 border border-slate-800/50 px-4 py-3.5 text-left transition hover:bg-slate-800/70 hover:border-slate-700/50"
                      onClick={() => {
                        window.scrollTo({ top: 0, behavior: "smooth" });
                        const next = [...movies];
                        [next[0], next[index]] = [next[index], next[0]];
                        setMovies(next);
                      }}
                    >
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-sm font-semibold text-white">{movie.title}</span>
                        {movie.rating_value > 0 && (
                          <>
                            <span className="text-slate-600">•</span>
                            <span className="text-sm text-cyan-400">⭐ {movie.rating_value.toFixed(1)}</span>
                          </>
                        )}
                      </div>
                      <div className="flex flex-wrap items-center gap-2 text-xs text-slate-400">
                        {movie.genres?.slice(0, 2).map((g) => (
                          <span key={g} className="text-cyan-300">{g}</span>
                        ))}
                        {movie.year && <span>• {movie.year}</span>}
                        {movie.runtime > 0 && <span>• {movie.runtime} min</span>}
                        {movie.rating && movie.rating !== "Unrated" && <span>• {movie.rating}</span>}
                      </div>
                    </button>
              ))}
            </div>
              )}
            </section>
            </div>
        </div>
      </main>
    </div>
  );
}
