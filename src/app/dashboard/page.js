"use client";

import { useMemo, useState } from "react";

const genreOptions = [
  "Sci-fi",
  "Thriller",
  "Drama",
  "Comedy",
  "Animation",
  "Documentary",
];

const vibeOptions = [
  "Adventurous",
  "Edge-of-seat",
  "Feel-good",
  "Slow burn",
  "Mind-bender",
  "Mood boost",
];

const ratingOrder = { G: 1, PG: 2, "PG-13": 3, R: 4 };

const curatedPool = [
  {
    title: "Midnight Courier",
    genres: ["Thriller"],
    vibe: "Edge-of-seat",
    runtime: 112,
    rating: "PG-13",
    score: 92,
    synopsis:
      "A bike messenger uncovers a covert exchange that forces her into a frantic overnight sprint across the city.",
    cast: ["Ana Cruz", "Elijah Brooks"],
    director: "N. Hartmann",
  },
  {
    title: "Parallax Garden",
    genres: ["Sci-fi", "Drama"],
    vibe: "Mind-bender",
    runtime: 124,
    rating: "PG-13",
    score: 95,
    synopsis:
      "An architect discovers a lab that grows memories into living spaces, forcing her to design her own past.",
    cast: ["Mila Rhee", "Caleb Knox"],
    director: "Rumi Takeda",
  },
  {
    title: "Sunlit Alley",
    genres: ["Feel-good", "Comedy", "Drama"],
    vibe: "Feel-good",
    runtime: 103,
    rating: "PG",
    score: 88,
    synopsis:
      "A street food vendor and a retiree open a micro-restaurant that reunites a fractured neighborhood.",
    cast: ["Isabel Moreno", "Gianni Costa"],
    director: "Priya Raman",
  },
  {
    title: "Horizon Sketches",
    genres: ["Documentary"],
    vibe: "Slow burn",
    runtime: 96,
    rating: "G",
    score: 86,
    synopsis:
      "Portraits of five indie artists capturing sunrise every morning for a year to document creative discipline.",
    cast: ["Documentary"],
    director: "Leah Sato",
  },
];

const favorites = {
  genres: ["Neo-noir", "Coming-of-age", "Historical epics"],
  actors: ["Tessa Lane", "Idris Cole", "Wen Li"],
  directors: ["Ava Martin", "Jonas K", "Mara Ito"],
};

const reviewFeed = [
  {
    film: "Parallax Garden",
    quote: "The set design earns every surreal turn. Felt handcrafted but sleek.",
    score: 4.7,
    user: "Lena D",
  },
  {
    film: "Midnight Courier",
    quote: "Lean, tense, and the city feels like a character driving the plot.",
    score: 4.4,
    user: "Qian L",
  },
  {
    film: "Sunlit Alley",
    quote: "Soft edges without losing momentum. Perfect Sunday watch.",
    score: 4.3,
    user: "Mase M",
  },
];

const users = [
  {
    user_id: "U-1842",
    user_name: "Elliot Rivers",
    email: "elliot@watch.me",
    password: "argon2id$demo$9c1b",
  },
];

const previousSearches = [
  {
    user_id: "U-1842",
    search_id: "S-561",
    prev_director: "Rumi Takeda",
    prev_genre: "Sci-fi",
    prev_decade: "2010s",
  },
  {
    user_id: "U-1842",
    search_id: "S-562",
    prev_director: "N. Hartmann",
    prev_genre: "Thriller",
    prev_decade: "2020s",
  },
  {
    user_id: "U-1842",
    search_id: "S-563",
    prev_director: "Priya Raman",
    prev_genre: "Comedy",
    prev_decade: "2010s",
  },
];

const favoriteTable = [
  { user_id: "U-1842", fav_director: "Rumi Takeda", fav_genre: "Sci-fi", fav_decade: "2010s" },
  { user_id: "U-1842", fav_director: "Priya Raman", fav_genre: "Comedy", fav_decade: "2020s" },
  { user_id: "U-1842", fav_director: "Ava Martin", fav_genre: "Drama", fav_decade: "1990s" },
];

const directors = [
  { director_id: "D-101", director_name: "N. Hartmann" },
  { director_id: "D-102", director_name: "Rumi Takeda" },
  { director_id: "D-103", director_name: "Priya Raman" },
  { director_id: "D-104", director_name: "Leah Sato" },
];

const genresTable = [
  { genre_id: "G-1", genre_name: "Sci-fi" },
  { genre_id: "G-2", genre_name: "Thriller" },
  { genre_id: "G-3", genre_name: "Comedy" },
  { genre_id: "G-4", genre_name: "Drama" },
  { genre_id: "G-5", genre_name: "Documentary" },
];

const actors = [
  { actor_id: "A-201", name: "Ana Cruz" },
  { actor_id: "A-202", name: "Elijah Brooks" },
  { actor_id: "A-203", name: "Mila Rhee" },
  { actor_id: "A-204", name: "Caleb Knox" },
  { actor_id: "A-205", name: "Isabel Moreno" },
  { actor_id: "A-206", name: "Gianni Costa" },
];

const languages = [
  { language_id: "L-1", language_name: "English" },
  { language_id: "L-2", language_name: "Spanish" },
  { language_id: "L-3", language_name: "Japanese" },
];

const films = [
  {
    film_id: "F-101",
    film_name: "Midnight Courier",
    director_id: "D-101",
    year: 2023,
    runtime: 112,
    genre_id: "G-2",
    language_id: "L-1",
  },
  {
    film_id: "F-102",
    film_name: "Parallax Garden",
    director_id: "D-102",
    year: 2022,
    runtime: 124,
    genre_id: "G-1",
    language_id: "L-3",
  },
  {
    film_id: "F-103",
    film_name: "Sunlit Alley",
    director_id: "D-103",
    year: 2020,
    runtime: 103,
    genre_id: "G-3",
    language_id: "L-2",
  },
  {
    film_id: "F-104",
    film_name: "Horizon Sketches",
    director_id: "D-104",
    year: 2019,
    runtime: 96,
    genre_id: "G-5",
    language_id: "L-1",
  },
];

const movieRatings = [
  {
    film_id: "F-101",
    user_id: "U-1842",
    user_rating: 4.5,
    user_review: "Lean and urgent. Loved the night pacing.",
  },
  {
    film_id: "F-102",
    user_id: "U-1842",
    user_rating: 4.8,
    user_review: "Gorgeous production design with a tight script.",
  },
  {
    film_id: "F-103",
    user_id: "U-1842",
    user_rating: 4.2,
    user_review: "Comfort watch with real heart.",
  },
];

const averageRatings = [
  { film_id: "F-101", average_score: 4.4 },
  { film_id: "F-102", average_score: 4.7 },
  { film_id: "F-103", average_score: 4.3 },
  { film_id: "F-104", average_score: 4.1 },
];

const actedIn = [
  { film_id: "F-101", actor_id: "A-201" },
  { film_id: "F-101", actor_id: "A-202" },
  { film_id: "F-102", actor_id: "A-203" },
  { film_id: "F-102", actor_id: "A-204" },
  { film_id: "F-103", actor_id: "A-205" },
  { film_id: "F-103", actor_id: "A-206" },
];

function Pill({ label, active, onClick, accent = "bg-cyan-400", variant = "default" }) {
  const baseStyles = "group flex items-center gap-2 rounded-lg border px-3.5 py-2 text-sm font-medium transition";
  
  if (variant === "chip") {
    return (
      <button
        onClick={onClick}
        className={`rounded-md border px-2.5 py-1.5 text-xs font-medium transition ${
          active
            ? "border-emerald-400/60 bg-emerald-500/20 text-emerald-50 shadow-sm shadow-emerald-500/10"
            : "border-slate-700/50 bg-slate-800/50 text-slate-300 hover:border-slate-600 hover:bg-slate-700/50 hover:text-white"
        }`}
      >
        {label}
      </button>
    );
  }
  
  return (
    <button
      onClick={onClick}
      className={`${baseStyles} ${
        active
          ? "border-cyan-400/60 bg-cyan-500/20 text-cyan-50 shadow-sm shadow-cyan-500/20"
          : "border-slate-700/50 bg-slate-800/50 text-slate-300 hover:border-slate-600 hover:bg-slate-700/50 hover:text-white"
      }`}
    >
      <span
        className={`h-2 w-2 rounded-full transition ${active ? accent : "bg-slate-500"}`}
      />
      {label}
    </button>
  );
}

function SectionCard({ title, children, dense = false, className = "" }) {
  return (
    <div
      className={`rounded-xl border border-slate-800/50 bg-slate-900/60 backdrop-blur-sm shadow-lg ${
        dense ? "p-5" : "p-6"
      } ${className}`}
    >
      {title && (
        <h3 className="mb-4 text-lg font-semibold text-white">{title}</h3>
      )}
      {children}
    </div>
  );
}

export default function DashboardPage() {
  const [genre, setGenre] = useState("Sci-fi");
  const [vibe, setVibe] = useState("Adventurous");
  const [runtime, setRuntime] = useState(115);
  const [maxRating, setMaxRating] = useState("PG-13");
  const [showFilters, setShowFilters] = useState(false);
  const [selectedActors, setSelectedActors] = useState([]);
  const [selectedDirectors, setSelectedDirectors] = useState([]);
  const [yearRange, setYearRange] = useState([2010, 2024]);
  const [minRating, setMinRating] = useState(0);

  const directorLookup = useMemo(
    () =>
      Object.fromEntries(
        directors.map((director) => [director.director_id, director.director_name])
      ),
    []
  );
  const genreLookup = useMemo(
    () =>
      Object.fromEntries(genresTable.map((genre) => [genre.genre_id, genre.genre_name])),
    []
  );
  const languageLookup = useMemo(
    () =>
      Object.fromEntries(
        languages.map((language) => [language.language_id, language.language_name])
      ),
    []
  );
  const actorLookup = useMemo(
    () => Object.fromEntries(actors.map((actor) => [actor.actor_id, actor.name])),
    []
  );
  const filmLookup = useMemo(
    () => Object.fromEntries(films.map((film) => [film.film_id, film])),
    []
  );

  const recommendation = useMemo(() => {
    const filtered = curatedPool.filter(
      (movie) =>
        movie.genres.includes(genre) &&
        movie.vibe === vibe &&
        ratingOrder[movie.rating] <= ratingOrder[maxRating]
    );

    return filtered[0] ?? curatedPool[0];
  }, [genre, maxRating, vibe]);

  const matchConfidence = useMemo(() => {
    const base = recommendation.score;
    const runtimePenalty = Math.abs(recommendation.runtime - runtime) * 0.35;
    return Math.min(99, Math.max(70, Math.round(base - runtimePenalty)));
  }, [recommendation, runtime]);

  const toggleActor = (actorName) => {
    setSelectedActors(prev =>
      prev.includes(actorName)
        ? prev.filter(a => a !== actorName)
        : [...prev, actorName]
    );
  };

  const toggleDirector = (directorName) => {
    setSelectedDirectors(prev =>
      prev.includes(directorName)
        ? prev.filter(d => d !== directorName)
        : [...prev, directorName]
    );
  };

  return (
    <div className="relative min-h-screen overflow-hidden bg-gradient-to-b from-slate-950 via-slate-950 to-slate-900 text-slate-50">
      <div className="pointer-events-none fixed inset-0">
        <div className="absolute left-0 top-0 h-96 w-96 rounded-full bg-cyan-500/8 blur-[120px]" />
        <div className="absolute right-0 top-1/4 h-80 w-80 rounded-full bg-indigo-500/8 blur-[100px]" />
        <div className="absolute bottom-0 left-1/3 h-64 w-64 rounded-full bg-purple-500/6 blur-[80px]" />
      </div>

      <header className="relative z-10 mx-auto max-w-7xl px-6 pt-10 pb-12">
        <div className="flex items-center gap-3">
          <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-cyan-400 via-cyan-500 to-indigo-500 text-slate-950 font-bold text-lg shadow-lg shadow-cyan-500/30">
            W
          </div>
          <div>
            <h1 className="text-2xl font-semibold text-white">WhatToWatch</h1>
            <p className="text-sm text-slate-400 mt-0.5">Find your next favorite film</p>
          </div>
        </div>
      </header>

      <main className="relative z-10 mx-auto max-w-7xl px-6 pb-20">
        <div className="grid gap-6 lg:grid-cols-[1.1fr,1fr,0.9fr]">
          {/* Left Column: Search Preferences */}
          <div className="space-y-6">
            <div>
              <h2 className="text-2xl font-semibold text-white mb-1.5">What are you in the mood for?</h2>
              <p className="text-slate-400 text-sm">Select your preferences to find the perfect match</p>
            </div>

            <SectionCard>
              <div className="space-y-6">
                <div className="space-y-3">
                  <label className="block text-sm font-medium text-white">Genre</label>
                  <div className="flex flex-wrap gap-2">
                    {genreOptions.map((option) => (
                      <Pill
                        key={option}
                        label={option}
                        active={genre === option}
                        onClick={() => setGenre(option)}
                      />
                    ))}
                  </div>
                </div>

                <div className="space-y-3">
                  <label className="block text-sm font-medium text-white">Vibe</label>
                  <div className="flex flex-wrap gap-2">
                    {vibeOptions.map((option) => (
                      <Pill
                        key={option}
                        label={option}
                        active={vibe === option}
                        accent="bg-indigo-400"
                        onClick={() => setVibe(option)}
                      />
                    ))}
                  </div>
                </div>

                <div className="grid gap-4 sm:grid-cols-2">
                  <div className="space-y-2">
                    <label className="block text-sm font-medium text-white">Max rating</label>
                    <select
                      value={maxRating}
                      onChange={(e) => setMaxRating(e.target.value)}
                      className="w-full rounded-lg border border-slate-700 bg-slate-800/50 px-4 py-2.5 text-sm text-white outline-none transition focus:border-cyan-400/60 focus:bg-slate-800 focus:ring-1 focus:ring-cyan-400/30"
                    >
                      {Object.keys(ratingOrder).map((rating) => (
                        <option
                          key={rating}
                          value={rating}
                          className="bg-slate-900 text-white"
                        >
                          Up to {rating}
                        </option>
                      ))}
                    </select>
                  </div>
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <label className="block text-sm font-medium text-white">Runtime</label>
                      <span className="text-sm font-medium text-cyan-400">{runtime} min</span>
                    </div>
                    <input
                      type="range"
                      min="85"
                      max="150"
                      value={runtime}
                      onChange={(e) => setRuntime(Number(e.target.value))}
                      className="h-2 w-full cursor-pointer appearance-none rounded-full bg-slate-800 accent-cyan-400"
                    />
                    <div className="flex justify-between text-xs text-slate-500">
                      <span>85 min</span>
                      <span>150 min</span>
                    </div>
                  </div>
                </div>
              </div>
            </SectionCard>
          </div>

          {/* Middle Column: Recommendation */}
          <div>
            <SectionCard>
              <div className="space-y-4">
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1">
                    <div className="mb-3 flex items-center gap-2">
                      <span className="rounded-full bg-indigo-500/20 px-2.5 py-1 text-xs font-medium text-indigo-300 border border-indigo-500/30">
                        {recommendation.vibe}
                      </span>
                      <span className="text-xs text-slate-500">•</span>
                      <span className="text-xs font-medium text-emerald-400">{matchConfidence}% match</span>
                    </div>
                    <h3 className="text-2xl font-semibold text-white mb-2">{recommendation.title}</h3>
                    <p className="text-sm text-slate-300 leading-relaxed">{recommendation.synopsis}</p>
                  </div>
                </div>

                <div className="flex flex-wrap gap-2">
                  {recommendation.genres.map((g) => (
                    <span
                      key={g}
                      className="rounded-lg bg-cyan-500/15 px-3 py-1.5 text-xs font-medium text-cyan-200 border border-cyan-500/20"
                    >
                      {g}
                    </span>
                  ))}
                  <span className="rounded-lg border border-slate-700 bg-slate-800/50 px-3 py-1.5 text-xs text-slate-300">
                    {recommendation.rating}
                  </span>
                  <span className="rounded-lg border border-slate-700 bg-slate-800/50 px-3 py-1.5 text-xs text-slate-300">
                    {recommendation.runtime} min
                  </span>
                </div>

                <div className="rounded-xl border border-slate-800 bg-slate-800/30 p-4 space-y-3">
                  <div>
                    <p className="text-xs text-slate-400 mb-1.5 font-medium">Cast</p>
                    <p className="text-sm font-medium text-white">
                      {recommendation.cast.join(" • ")}
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-slate-400 mb-1.5 font-medium">Director</p>
                    <p className="text-sm font-medium text-white">
                      {recommendation.director}
                    </p>
                  </div>
                </div>

                <div className="flex gap-3">
                  <button className="flex-1 rounded-lg bg-gradient-to-r from-cyan-400 to-indigo-500 px-4 py-3 text-sm font-semibold text-slate-950 transition hover:shadow-lg hover:shadow-cyan-500/40 hover:scale-[1.02] active:scale-[0.98]">
                    Add to Queue
                  </button>
                  <button className="rounded-lg border border-slate-700 px-4 py-3 text-sm font-medium text-slate-200 transition hover:border-slate-600 hover:bg-slate-800/50 hover:text-white">
                    Find Another
                  </button>
                </div>
              </div>
            </SectionCard>
          </div>

          {/* Right Column: Filters */}
          <div>
            <SectionCard className={`border-emerald-500/30 bg-gradient-to-br from-slate-900/60 to-slate-900/40 transition-all ${showFilters ? "shadow-xl shadow-emerald-500/10" : ""}`}>
              <button
                onClick={() => setShowFilters(!showFilters)}
                className="flex w-full items-center justify-between text-left group mb-4"
              >
                <div className="flex items-center gap-3">
                  <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-emerald-500/20 border border-emerald-500/30 group-hover:bg-emerald-500/30 transition">
                    <svg className="h-4 w-4 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
                    </svg>
                  </div>
                  <div>
                    <h3 className="text-base font-semibold text-white">Refine Search</h3>
                    <p className="text-xs text-slate-400">Fine-tune results</p>
                  </div>
                </div>
                <div className={`transition-transform duration-200 ${showFilters ? "rotate-180" : ""}`}>
                  <svg className="h-4 w-4 text-slate-400 group-hover:text-emerald-400 transition" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                </div>
              </button>

              {showFilters && (
                <div className="space-y-5 pt-4 border-t border-slate-800">
                  <div className="space-y-2.5">
                    <label className="block text-xs font-medium text-white">Actors</label>
                    <div className="flex flex-wrap gap-1.5">
                      {actors.map((actor) => (
                        <Pill
                          key={actor.actor_id}
                          label={actor.name}
                          active={selectedActors.includes(actor.name)}
                          onClick={() => toggleActor(actor.name)}
                          variant="chip"
                        />
                      ))}
                    </div>
                  </div>

                  <div className="space-y-2.5">
                    <label className="block text-xs font-medium text-white">Directors</label>
                    <div className="flex flex-wrap gap-1.5">
                      {directors.map((director) => (
                        <Pill
                          key={director.director_id}
                          label={director.director_name}
                          active={selectedDirectors.includes(director.director_name)}
                          onClick={() => toggleDirector(director.director_name)}
                          variant="chip"
                        />
                      ))}
                    </div>
                  </div>

                  <div className="space-y-2.5">
                    <label className="block text-xs font-medium text-white">Year Range</label>
                    <div className="grid grid-cols-2 gap-3">
                      <div>
                        <label className="block text-[10px] text-slate-400 mb-1">From</label>
                        <input
                          type="number"
                          min="1900"
                          max="2024"
                          value={yearRange[0]}
                          onChange={(e) => setYearRange([Number(e.target.value), yearRange[1]])}
                          className="w-full rounded-lg border border-slate-700 bg-slate-800/50 px-2.5 py-2 text-xs text-white outline-none transition focus:border-emerald-400/60 focus:bg-slate-800"
                        />
                      </div>
                      <div>
                        <label className="block text-[10px] text-slate-400 mb-1">To</label>
                        <input
                          type="number"
                          min="1900"
                          max="2024"
                          value={yearRange[1]}
                          onChange={(e) => setYearRange([yearRange[0], Number(e.target.value)])}
                          className="w-full rounded-lg border border-slate-700 bg-slate-800/50 px-2.5 py-2 text-xs text-white outline-none transition focus:border-emerald-400/60 focus:bg-slate-800"
                        />
                      </div>
                    </div>
                  </div>

                  <div className="space-y-2.5">
                    <div className="flex items-center justify-between">
                      <label className="block text-xs font-medium text-white">Min Rating</label>
                      <span className="text-xs text-slate-400">{minRating > 0 ? `${minRating}/5` : "Any"}</span>
                    </div>
                    <input
                      type="range"
                      min="0"
                      max="5"
                      step="0.5"
                      value={minRating}
                      onChange={(e) => setMinRating(Number(e.target.value))}
                      className="h-1.5 w-full cursor-pointer appearance-none rounded-full bg-slate-800 accent-emerald-400"
                    />
                    <div className="flex justify-between text-[10px] text-slate-500">
                      <span>Any</span>
                      <span>5.0</span>
                    </div>
                  </div>

                  <div className="flex gap-2 pt-1">
                    <button
                      onClick={() => {
                        setSelectedActors([]);
                        setSelectedDirectors([]);
                        setYearRange([2010, 2024]);
                        setMinRating(0);
                      }}
                      className="flex-1 rounded-lg border border-slate-700 px-3 py-2 text-xs font-medium text-slate-300 transition hover:border-slate-600 hover:bg-slate-800/50 hover:text-white"
                    >
                      Clear
                    </button>
                    <button
                      onClick={() => setShowFilters(false)}
                      className="flex-1 rounded-lg bg-gradient-to-r from-emerald-500 to-teal-500 px-3 py-2 text-xs font-semibold text-white transition hover:shadow-lg hover:shadow-emerald-500/30 hover:scale-[1.02] active:scale-[0.98]"
                    >
                      Apply
                    </button>
                  </div>
                </div>
              )}
            </SectionCard>
          </div>
        </div>
      </main>
    </div>
  );
}
