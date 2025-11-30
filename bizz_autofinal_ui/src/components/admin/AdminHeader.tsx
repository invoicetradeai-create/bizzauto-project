"use client";

import { useState, useEffect } from "react";
import { Bell, Sparkles, Menu, Sun, Moon } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { useTheme } from "@/hooks/use-theme";
import { getAuthHeaders } from "@/lib/auth";

interface AdminHeaderProps {
    onMenuClick: () => void;
}

export function AdminHeader({ onMenuClick }: AdminHeaderProps) {
    const [initial, setInitial] = useState("?");
    const [name, setName] = useState("Admin User");
    const { theme, toggleTheme, mounted } = useTheme();

    useEffect(() => {
        const fetchUser = async () => {
            try {
                const headers = await getAuthHeaders();
                const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/users/me`, {
                    headers
                });
                if (res.ok) {
                    const data = await res.json();
                    const displayName = data.full_name || data.email || "Admin";
                    setName(displayName);
                    setInitial(displayName.charAt(0).toUpperCase());
                }
            } catch (error) {
                console.error("Failed to fetch user info", error);
            }
        };

        fetchUser();
    }, []);

    return (
        <header className="bg-white dark:bg-slate-900 border-b border-gray-200 dark:border-slate-800 h-16 flex items-center justify-between px-6 sticky top-0 z-40 transition-colors duration-300">
            {/* Left Side: Mobile Menu & Brand (Visible on mobile only or if needed) */}
            <div className="flex items-center gap-4">
                <button
                    onClick={onMenuClick}
                    className="md:hidden text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white"
                >
                    <Menu size={24} />
                </button>

                {/* Optional: Show Logo here if not in sidebar, or just title */}
                <div className="md:hidden flex items-center gap-2">
                    <div className="h-8 w-8 rounded-full flex items-center justify-center bg-blue-600">
                        <Sparkles className="h-4 w-4 text-white" />
                    </div>
                    <span className="font-bold text-gray-800 dark:text-white">BizzAuto</span>
                </div>
            </div>

            {/* Right Side: Actions */}
            <div className="flex items-center gap-4 ml-auto">
                {/* Theme Toggle */}
                {mounted && (
                    <Button
                        variant="ghost"
                        size="icon"
                        onClick={toggleTheme}
                        className="text-gray-500 dark:text-gray-400 hover:text-blue-600 dark:hover:text-blue-400 transition-colors"
                    >
                        {theme === "dark" ? (
                            <Sun className="w-5 h-5" />
                        ) : (
                            <Moon className="w-5 h-5" />
                        )}
                    </Button>
                )}

                <Button variant="ghost" size="icon" className="relative text-gray-500 dark:text-gray-400 hover:text-blue-600 dark:hover:text-blue-400">
                    <Bell size={20} />
                    <span className="absolute top-2 right-2 h-2 w-2 bg-red-500 rounded-full border border-white dark:border-slate-900"></span>
                </Button>

                <div className="flex items-center gap-3 pl-4 border-l border-gray-200 dark:border-slate-800">
                    <div className="text-right hidden sm:block">
                        <p className="text-sm font-medium text-gray-900 dark:text-gray-100">{name}</p>
                        <p className="text-xs text-gray-500 dark:text-gray-400">Super Admin</p>
                    </div>
                    <Avatar className="h-9 w-9 cursor-pointer border-2 border-transparent hover:border-blue-500 transition-all">
                        <AvatarFallback className="bg-blue-600 text-white font-bold">
                            {initial}
                        </AvatarFallback>
                    </Avatar>
                </div>
            </div>
        </header>
    );
}
