"use client";

import { useState } from "react";
import Link from "next/link";
import { Menu, Sparkles, Sun, Moon } from "lucide-react";
import {
  Sheet,
  SheetContent,
  SheetTrigger,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet";
import { Button } from "@/components/ui/button";
import { navLinks } from "@/app/data/navlinks";
import { useTheme } from "@/hooks/use-theme";

const Header = () => {
  const [open, setOpen] = useState(false);
  const { theme, toggleTheme, mounted } = useTheme();

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 bg-blue-50/90 dark:bg-blue-900/90 backdrop-blur-md border-b border-blue-200 dark:border-blue-700 shadow-sm transition-colors">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          {/* ================= Logo ================= */}
          <div className="flex items-center gap-3">
<div className="h-10 w-10 rounded-full flex items-center justify-center bg-gradient-to-br from-blue-500 to-blue-700 hover:from-blue-600 hover:to-blue-800 shadow-lg transition-all duration-300">
  <Sparkles className="h-5 w-5 text-white" />
</div>

            <span className="text-2xl font-extrabold text-blue-700 dark:text-blue-200 tracking-wide">
              BizzAuto
            </span>
          </div>

          {/* ================= Desktop Navigation ================= */}
          <div className="hidden md:flex items-center gap-6">
            {navLinks.map((link) => (
              <a
                key={link.href}
                href={link.href}
                className="text-sm font-medium text-blue-700 dark:text-blue-200 hover:text-blue-500 dark:hover:text-blue-400 transition-colors"
              >
                {link.label}
              </a>
            ))}
          </div>

          {/* ================= Right Side Buttons ================= */}
          <div className="flex items-center gap-2 md:gap-4">


            {/* Theme Toggle */}
            {mounted && (
              <Button
                variant="ghost"
                size="icon"
                onClick={toggleTheme}
                className="hidden sm:inline-flex text-blue-700 dark:text-blue-200 hover:text-blue-500 dark:hover:text-blue-400 transition-colors"
              >
                {theme === "dark" ? (
                  <Sun className="w-4 h-4" />
                ) : (
                  <Moon className="w-4 h-4" />
                )}
              </Button>
            )}

         {/* Desktop Buttons (Hidden on mobile) */}
<div className="hidden md:flex items-center gap-3">
  <Link href="/signin">
    <Button className="bg-blue-600 text-white hover:bg-blue-700 py-2 px-4">
      Sign In
    </Button>
  </Link>
  <Link href="/signUp">
    <Button className="inline-flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-blue-500 to-blue-700 text-white rounded-md shadow-md hover:brightness-95 transition-all">
      <Sparkles className="w-4 h-4" />
      <span className="text-sm font-medium">Get Started Free</span>
    </Button>
  </Link>
</div>

{/* Mobile Menu Trigger */}
<div className="md:hidden">
  <Sheet open={open} onOpenChange={setOpen}>
    <SheetTrigger asChild>
      <Button
        variant="ghost"
        size="icon"
        className="text-blue-600 fixed top-4 right-4 z-50"
      >
        <Menu className="h-6 w-6" />
      </Button>
    </SheetTrigger>

    <SheetContent
      side="right"
      className="w-full max-w-[360px] bg-blue-50 dark:bg-blue-900 p-6 shadow-xl"
    >
      <SheetHeader>
        <SheetTitle className="text-xl font-bold text-blue-700 dark:text-blue-200">
          Menu
        </SheetTitle>
      </SheetHeader>

      <nav className="flex flex-col gap-4 mt-4">
        {navLinks.map((link) => (
          <a
            key={link.href}
            href={link.href}
            onClick={() => setOpen(false)}
            className="text-lg font-medium text-blue-700 dark:text-blue-200 hover:text-blue-500 dark:hover:text-blue-400 transition-colors py-2 px-3 rounded-md hover:bg-blue-100 dark:hover:bg-blue-800"
          >
            {link.label}
          </a>
        ))}

        {/* Theme Toggle (Mobile) */}
        {mounted && (
          <Button
            variant="ghost"
            onClick={() => {
              toggleTheme();
              setOpen(false);
            }}
            className="w-full justify-start text-blue-700 dark:text-blue-200 mt-2 px-3 py-2 rounded-md hover:bg-blue-100 dark:hover:bg-blue-800 flex items-center gap-2 transition-colors"
          >
            {theme === "dark" ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
            {theme === "dark" ? "Light Mode" : "Dark Mode"}
          </Button>
        )}

        {/* Mobile Auth Buttons */}
        <div className="flex flex-col gap-3 mt-6 pt-4 border-t border-blue-200 dark:border-blue-700">
          <Link href="/signin" onClick={() => setOpen(false)}>
            <Button className="w-full bg-blue-600 text-white hover:bg-blue-700 transition-colors py-2">
              Sign In
            </Button>
          </Link>
          <Link href="/signUp" onClick={() => setOpen(false)}>
            <Button className="w-full bg-gradient-to-r from-blue-500 to-blue-700 text-white hover:brightness-95 transition-all py-2 flex items-center justify-center gap-2">
              <Sparkles className="w-5 h-5" />
              Get Started
            </Button>
          </Link>
        </div>
      </nav>
    </SheetContent>
  </Sheet>
</div>

          </div>
        </div>
      </div>
    </nav>
  );
};

export default Header;
