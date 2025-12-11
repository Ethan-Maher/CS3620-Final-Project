"use client";

import { useState, useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import Link from "next/link";
import { api } from "@/lib/api";
import Navbar from "@/components/Navbar";

export default function ReviewsPage() {
  const [activeTab, setActiveTab] = useState("movies");
  const [reviews, setReviews] = useState([]);
  const [selectedItem, setSelectedItem] = useState(null);
  const [rating, setRating] = useState(5);
  const [reviewText, setReviewText] = useState("");
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const router = useRouter();
  const searchParams = useSearchParams();

  useEffect(() => {
    const filmId = searchParams?.get("film_id");
    const showId = searchParams?.get("show_id");
    if (filmId) {
      setActiveTab("movies");
      setSelectedItem({ id: parseInt(filmId), type: "movie" });
      fetchReviews(parseInt(filmId), "movie");
    } else if (showId) {
      setActiveTab("shows");
      setSelectedItem({ id: parseInt(showId), type: "show" });
      fetchReviews(parseInt(showId), "show");
    } else {
      fetchAllReviews();
    }
  }, [searchParams]);

  const fetchReviews = async (id, type) => {
    setLoading(true);
    setError("");
    try {
      const url = type === "movie" ? api.movieReviews(id) : api.showReviews(id);
      const response = await fetch(url, {
        credentials: "include",
      });
      const data = await response.json();
      if (data.success) {
        setReviews(data.reviews || []);
      } else {
        setError(data.error || "Failed to load reviews");
      }
    } catch (err) {
      setError("Failed to load reviews");
    } finally {
      setLoading(false);
    }
  };

  const fetchAllReviews = async () => {
    setLoading(true);
    try {
      const url = activeTab === "movies" ? api.movieReviews() : api.showReviews();
      const response = await fetch(url, {
        credentials: "include",
      });
      const data = await response.json();
      if (data.success) {
        setReviews(data.reviews || []);
      }
    } catch (err) {
      setError("Failed to load reviews");
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!selectedItem) {
      setError("Please select a movie or show to review");
      return;
    }

    setSubmitting(true);
    setError("");
    setSuccess("");

    try {
      const user = JSON.parse(localStorage.getItem("user") || "{}");
      if (!user.user_id) {
        router.push("/signin");
        return;
      }

      const url = selectedItem.type === "movie" 
        ? api.movieReviews(selectedItem.id) 
        : api.showReviews(selectedItem.id);
      
      const response = await fetch(url, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        credentials: "include",
        body: JSON.stringify({
          rating: rating,
          review: reviewText,
        }),
      });

      const data = await response.json();
      if (data.success) {
        setSuccess("Review posted successfully!");
        setReviewText("");
        setRating(5);
        fetchReviews(selectedItem.id, selectedItem.type);
        setTimeout(() => setSuccess(""), 3000);
      } else {
        setError(data.error || "Failed to post review");
      }
    } catch (err) {
      setError("Network error. Please try again.");
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (reviewId, itemId, type) => {
    if (!confirm("Are you sure you want to delete this review?")) return;

    try {
      const url = type === "movie" ? api.movieReviews(itemId) : api.showReviews(itemId);
      const response = await fetch(url, {
        method: "DELETE",
        credentials: "include",
      });
      const data = await response.json();
      if (data.success) {
        fetchReviews(itemId, type);
      }
    } catch (err) {
      setError("Failed to delete review");
    }
  };

  const user = typeof window !== "undefined" ? JSON.parse(localStorage.getItem("user") || "{}") : {};

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#0a0e1a] via-[#141827] to-[#0f1525] text-[#e8eaf6]">
      <Navbar 
        pageTitle="Reviews"
        pageSubtitle="Share your thoughts"
      />

      <main className="mx-auto max-w-7xl px-6 py-8">
        <div className="mb-6 flex gap-2 border-b border-red-900/20">
          <button
            onClick={() => {
              setActiveTab("movies");
              fetchAllReviews();
            }}
            className={`px-6 py-3 text-sm font-medium transition ${
              activeTab === "movies"
                ? "border-b-2 border-red-400 text-red-300"
                : "text-gray-400 hover:text-gray-300"
            }`}
          >
            Movie Reviews
          </button>
          <button
            onClick={() => {
              setActiveTab("shows");
              fetchAllReviews();
            }}
            className={`px-6 py-3 text-sm font-medium transition ${
              activeTab === "shows"
                ? "border-b-2 border-red-400 text-red-300"
                : "text-gray-400 hover:text-gray-300"
            }`}
          >
            Show Reviews
          </button>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Review Form */}
          <div className="lg:col-span-1">
            <div className="rounded-xl bg-[#141827]/60 border border-red-900/20 p-6 shadow-xl shadow-black/30 backdrop-blur-sm sticky top-24">
              <h2 className="text-lg font-semibold text-white mb-4">Write a Review</h2>
              
              {!user.user_id ? (
                <div className="text-center py-8">
                  <p className="text-sm text-gray-400 mb-4">Please sign in to write reviews</p>
                  <Link
                    href="/signin"
                    className="inline-block px-4 py-2 rounded-lg bg-gradient-to-r from-red-500 to-red-600 text-white hover:from-red-600 hover:to-red-700 transition text-sm font-medium"
                  >
                    Sign In
                  </Link>
                </div>
              ) : (
                <form onSubmit={handleSubmit} className="space-y-4">
                  {error && (
                    <div className="p-3 rounded-lg bg-red-500/10 border border-red-500/30 text-red-400 text-sm">
                      {error}
                    </div>
                  )}
                  {success && (
                    <div className="p-3 rounded-lg bg-green-500/10 border border-green-500/30 text-green-400 text-sm">
                      {success}
                    </div>
                  )}

                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      Rating (1-10)
                    </label>
                    <input
                      type="number"
                      min="1"
                      max="10"
                      value={rating}
                      onChange={(e) => setRating(parseInt(e.target.value))}
                      className="w-full rounded-lg border border-red-900/30 bg-[#0a0e1a]/50 px-4 py-2.5 text-sm text-white focus:border-red-500 focus:outline-none focus:ring-2 focus:ring-red-500/30 transition"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      Review
                    </label>
                    <textarea
                      value={reviewText}
                      onChange={(e) => setReviewText(e.target.value)}
                      placeholder="Write your review here..."
                      rows="6"
                      className="w-full rounded-lg border border-red-900/30 bg-[#0a0e1a]/50 px-4 py-2.5 text-sm text-white placeholder-gray-500 focus:border-red-500 focus:outline-none focus:ring-2 focus:ring-red-500/30 transition resize-none"
                    />
                  </div>

                  {selectedItem && (
                    <div className="p-3 rounded-lg bg-red-500/10 border border-red-500/20">
                      <p className="text-xs text-red-300 font-medium mb-1">Reviewing:</p>
                      <p className="text-xs text-gray-300">
                        {activeTab === "movies" ? "Movie" : "Show"} ID: {selectedItem.id}
                      </p>
                    </div>
                  )}
                  
                  {!selectedItem && (
                    <div className="text-xs text-gray-400 p-3 rounded-lg bg-[#0a0e1a]/50 border border-red-900/20">
                      <p>Tip: To review a specific {activeTab === "movies" ? "movie" : "show"}, go to the dashboard and click "Review" on the item.</p>
                    </div>
                  )}

                  <button
                    type="submit"
                    disabled={submitting || !selectedItem}
                    className="w-full rounded-lg bg-gradient-to-r from-red-500 to-red-600 px-4 py-2.5 text-sm font-medium text-white hover:from-red-600 hover:to-red-700 transition shadow-lg shadow-red-500/30 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {submitting ? "Posting..." : selectedItem ? "Post Review" : "Select Item to Review"}
                  </button>
                </form>
              )}
            </div>
          </div>

          {/* Reviews List */}
          <div className="lg:col-span-2">
            <div className="rounded-xl bg-gradient-to-br from-[#141827]/80 to-[#0a0e1a]/60 border border-red-900/30 p-6 shadow-xl shadow-black/40 backdrop-blur-sm">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-lg font-semibold text-white">
                  {selectedItem ? `Reviews for this ${selectedItem.type}` : `All ${activeTab === "movies" ? "Movie" : "Show"} Reviews`}
                </h2>
                {reviews.length > 0 && (
                  <span className="text-xs text-gray-400">{reviews.length} review{reviews.length !== 1 ? 's' : ''}</span>
                )}
              </div>

              {loading ? (
                <div className="flex items-center justify-center py-16">
                  <div className="h-8 w-8 animate-spin rounded-full border-3 border-red-400 border-t-transparent" />
                </div>
              ) : reviews.length === 0 ? (
                <div className="py-12 text-center">
                  <p className="text-sm text-gray-400">No reviews yet. Be the first to review!</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {reviews.map((review) => (
                    <div
                      key={review.review_id}
                      className="rounded-lg bg-[#0a0e1a]/60 border border-red-900/30 p-5 transition hover:bg-red-500/5 hover:border-red-500/40"
                    >
                      <div className="flex items-start justify-between gap-4 mb-3">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-2">
                            <span className="text-base font-semibold text-white">
                              {review.film_name || review.show_name}
                            </span>
                            <span className="text-xs text-gray-500">•</span>
                            <span className="text-sm text-gray-400">{review.user_email}</span>
                          </div>
                          <div className="flex items-center gap-3">
                            <span className="inline-flex items-center gap-1 px-2 py-1 rounded bg-red-500/20 text-red-300 text-sm font-medium">
                              {review.rating}/10
                            </span>
                          </div>
                        </div>
                        {user.user_id === review.user_id && (
                          <button
                            onClick={() => handleDelete(review.review_id, review.film_id || review.show_id, activeTab === "movies" ? "movie" : "show")}
                            className="px-3 py-1.5 rounded-lg text-xs font-medium text-red-400 hover:bg-red-500/10 border border-red-500/20 transition"
                          >
                            Delete
                          </button>
                        )}
                      </div>
                      {review.review && (
                        <p className="text-sm text-gray-300 leading-relaxed whitespace-pre-wrap">{review.review}</p>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

