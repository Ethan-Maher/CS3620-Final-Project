"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

export default function HomePage() {
  const router = useRouter();

  useEffect(() => {
    // Check if user is logged in
    const user = localStorage.getItem("user");
    if (user) {
      router.push("/dashboard");
    } else {
      router.push("/signin");
    }
  }, [router]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#0a0e1a] via-[#141827] to-[#0f1525] flex items-center justify-center">
      <div className="h-8 w-8 animate-spin rounded-full border-3 border-red-400 border-t-transparent" />
    </div>
  );
}
