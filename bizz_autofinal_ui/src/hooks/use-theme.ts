
"use client";

import { useState, useEffect, useCallback } from "react";

type Theme = "light" | "dark";

export function useTheme() {
  const [mounted, setMounted] = useState(false);
  
  // Safely get the initial theme on the client side only
  const [theme, setTheme] = useState<Theme>(() => {
    if (typeof window !== "undefined") {
      const stored = localStorage.getItem("theme") as Theme | null;
      if (stored) return stored;
      return window.matchMedia("(prefers-color-scheme: dark)").matches
        ? "dark"
        : "light";
    }
    // Default theme for server-side rendering
    return "light";
  });

  // Effect to apply the theme class to the document and save to localStorage
  useEffect(() => {
    if (mounted) {
      document.documentElement.classList.remove("light", "dark");
      document.documentElement.classList.add(theme);
      localStorage.setItem("theme", theme);
    }
  }, [theme, mounted]);

  // Effect to set mounted to true only on the client, after initial render
  useEffect(() => {
    setMounted(true);
  }, []);

  const toggleTheme = useCallback(() => {
    if (!mounted) return;
    setTheme((prevTheme) => (prevTheme === "dark" ? "light" : "dark"));
  }, [mounted]);

  return { theme, toggleTheme, mounted };
}
