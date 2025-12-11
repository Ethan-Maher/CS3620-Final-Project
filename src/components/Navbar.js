"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { api } from "@/lib/api";

export default function Navbar({ pageTitle, pageSubtitle, showStats, statsCount }) {
  const [user, setUser] = useState(null);
  const pathname = usePathname();

  useEffect(() => {
    const userData = localStorage.getItem("user");
    if (userData) {
      setUser(JSON.parse(userData));
    }
  }, []);

  const handleSignOut = async () => {
    try {
      await fetch(api.signout, {
        method: "POST",
        credentials: "include",
      });
    } catch (e) {}
    localStorage.removeItem("user");
    window.location.href = "/signin";
  };

  const isActive = (path) => pathname === path;

  return (
    <header className="border-b border-red-900/30 bg-[#0a0e1a]/95 backdrop-blur-xl sticky top-0 z-50 shadow-2xl shadow-black/50">
      <div className="mx-auto max-w-7xl px-6">
        <div className="flex items-center justify-between h-16">
          {/* Logo and Title */}
          <div className="flex items-center gap-4">
            <Link href="/dashboard" className="flex h-10 w-10 items-center justify-center rounded-lg bg-gradient-to-br from-red-500 via-red-600 to-red-700 text-white font-bold text-lg shadow-lg shadow-red-500/50 ring-1 ring-red-500/30 hover:scale-105 transition-transform">
              W
            </Link>
            <div className="hidden sm:block">
              <h1 className="text-lg font-bold text-white tracking-tight">{pageTitle || "WhatToWatch"}</h1>
              {pageSubtitle && (
                <p className="text-xs text-gray-400 mt-0.5">{pageSubtitle}</p>
              )}
            </div>
          </div>

          {/* Navigation Links */}
          <nav className="hidden md:flex items-center gap-1">
            <Link
              href="/dashboard"
              className={`px-4 py-2 rounded-lg text-sm font-medium transition ${
                isActive("/dashboard")
                  ? "text-red-400 bg-red-500/10"
                  : "text-gray-300 hover:text-white hover:bg-red-500/10"
              }`}
            >
              Dashboard
            </Link>
            <Link
              href="/watch-later"
              className={`px-4 py-2 rounded-lg text-sm font-medium transition ${
                isActive("/watch-later")
                  ? "text-red-400 bg-red-500/10"
                  : "text-gray-300 hover:text-white hover:bg-red-500/10"
              }`}
            >
              Watch Later
            </Link>
            <Link
              href="/favorites"
              className={`px-4 py-2 rounded-lg text-sm font-medium transition ${
                isActive("/favorites")
                  ? "text-red-400 bg-red-500/10"
                  : "text-gray-300 hover:text-white hover:bg-red-500/10"
              }`}
            >
              Favorites
            </Link>
            <Link
              href="/reviews"
              className={`px-4 py-2 rounded-lg text-sm font-medium transition ${
                isActive("/reviews")
                  ? "text-red-400 bg-red-500/10"
                  : "text-gray-300 hover:text-white hover:bg-red-500/10"
              }`}
            >
              Reviews
            </Link>
            <Link
              href="/audit-logs"
              className={`px-4 py-2 rounded-lg text-sm font-medium transition ${
                isActive("/audit-logs")
                  ? "text-red-400 bg-red-500/10"
                  : "text-gray-300 hover:text-white hover:bg-red-500/10"
              }`}
            >
              Logs
            </Link>
          </nav>

          {/* Right Side - Stats and User */}
          <div className="flex items-center gap-3">
            {showStats && statsCount !== undefined && statsCount > 0 && (
              <div className="hidden lg:flex items-center gap-2 px-3 py-1.5 rounded-lg bg-red-500/10 border border-red-500/20 backdrop-blur-sm">
                <span className="text-sm font-semibold text-red-400">{statsCount}</span>
                <span className="text-xs text-gray-400">{statsCount === 1 ? 'match' : 'matches'}</span>
              </div>
            )}
            
            {user?.user_id ? (
              <div className="flex items-center gap-3">
                <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-lg bg-red-500/10 border border-red-500/20">
                  <div className="h-2 w-2 rounded-full bg-red-400"></div>
                  <span className="text-xs font-medium text-gray-300">{user.email?.split("@")[0]}</span>
                </div>
                <button
                  onClick={handleSignOut}
                  className="px-4 py-1.5 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 hover:bg-red-500/20 hover:text-red-300 transition text-sm font-medium"
                >
                  Sign Out
                </button>
              </div>
            ) : (
              <Link
                href="/signin"
                className="px-4 py-1.5 rounded-lg bg-gradient-to-r from-red-500 to-red-600 text-white hover:from-red-600 hover:to-red-700 transition text-sm font-medium shadow-lg shadow-red-500/30"
              >
                Sign In
              </Link>
            )}

            {/* Mobile Menu Button */}
            <button className="md:hidden p-2 rounded-lg text-gray-400 hover:text-white hover:bg-red-500/10 transition">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </header>
  );
}

