
"use client";

import { useState, useEffect } from "react";

export function useTheme() {
  const getInitial = (): "light" | "dark" => {
    if (typeof window === "undefined") return "light";
    const stored = localStorage.getItem("theme") as "light" | "dark" | null;
    if (stored) {
      // ensure document class is in sync
      document.documentElement.classList.toggle("dark", stored === "dark");
      return stored;
    }
    const prefersDark = window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches;
    document.documentElement.classList.toggle("dark", prefersDark);
    return prefersDark ? "dark" : "light";
  };

  const [theme, setTheme] = useState<"light" | "dark">("light");
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    setTheme(getInitial());
  }, []);

  const toggleTheme = () => {
    if (!mounted) return;
    const next = theme === "dark" ? "light" : "dark";
    setTheme(next);
    localStorage.setItem("theme", next);
    document.documentElement.classList.toggle("dark", next === "dark");
  };

  return { theme, toggleTheme, mounted };
}
