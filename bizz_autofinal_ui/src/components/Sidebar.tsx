"use client";

import React from "react";
import { usePathname, useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { Sparkles, LayoutDashboard, Users, FileText, Package, MessageSquare, BarChart3, Settings, LogOut, Receipt, ScanLine } from "lucide-react";
import { apiClient } from "@/lib/api-client";
import { UUID } from "crypto";

const menuItems = [
  { name: "Dashboard", icon: LayoutDashboard, path: "/dashboard" },
  { name: "CRM", icon: Users, path: "/crm" },
  { name: "Invoices", icon: FileText, path: "/invoices" },
  { name: "Inventory", icon: Package, path: "/inventory" },
  { name: "Expense", icon: Receipt, path: "/expense" },
  { name: "WhatsApp", icon: MessageSquare, path: "/whatsapp" },
  { name: "Analytics", icon: BarChart3, path: "/analytics" },
  { name: "Accounting", icon: Receipt, path: "/accounting" }, // New item
  { name: "Settings", icon: Settings, path: "/settings" },
];


export const NavigationContent = ({ setOpen }: { setOpen?: (open: boolean) => void }) => {
  const router = useRouter();
  const pathname = usePathname();

  const handleNavigation = (path: string) => {
    router.push(path);
    if (setOpen) setOpen(false);
  };

  const logout = () => router.push("/signin");

  const [userName, setUserName] = React.useState<string>("User");
  const [userEmail, setUserEmail] = React.useState<string>("user@example.com");
  const [userRole, setUserRole] = React.useState<string>("User");
  const [avatarLetter, setAvatarLetter] = React.useState<string>("?");

  type UserType = { id: UUID; full_name: string; email: string; };

  React.useEffect(() => {
    const fetchCurrentUserData = async (userId: string) => {
      // Basic UUID validation regex
      const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
      
      if (!userId || !uuidRegex.test(userId)) {
        console.warn("Invalid or missing user ID, skipping fetch:", userId);
        return;
      }

      try {
        // Get the session token directly to ensure authentication
        const { data: { session } } = await import("@/lib/supabaseClient").then(mod => mod.supabase.auth.getSession());
        const token = session?.access_token;

        if (!token) {
          console.warn("No session token available, skipping fetch");
          return;
        }

        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/users/${userId}`, {
          headers: {
            "Authorization": `Bearer ${token}`,
            "Content-Type": "application/json",
          },
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const user: UserType = await response.json();
        if (user) {
          setUserName(user.full_name);
          setUserEmail(user.email);
          setAvatarLetter(user.full_name.charAt(0).toUpperCase());
          // Also update localStorage with fresh data
          localStorage.setItem("user_name", user.full_name);
          localStorage.setItem("user_email", user.email);
          localStorage.setItem("user_avatar", user.full_name.charAt(0));
        }
      } catch (error) {
        console.error("Failed to fetch current user data for sidebar:", error);
      }
    };

    // First, try to load from localStorage for instant UI update
    const name = localStorage.getItem("user_name");
    const email = localStorage.getItem("user_email");
    const role = localStorage.getItem("user_role"); // This is still not being fetched from the backend
    const avatar = localStorage.getItem("user_avatar");
    if (name) setUserName(name);
    if (email) setUserEmail(email);
    if (role) setUserRole(role);
    if (avatar) setAvatarLetter(avatar.toUpperCase());

    // Then, fetch from API to get the latest data for the logged-in user
    const userId = localStorage.getItem("user_id");
    if (userId) {
      fetchCurrentUserData(userId);
    }
  }, []);

  return (
    <div className="flex flex-col h-full overflow-hidden">
      <div className="p-3 sm:p-4 flex items-center gap-2 sm:gap-3 border-b bg-gradient-to-r from-blue-500/90 to-blue-600/90 dark:from-blue-700/80 dark:to-blue-800/80 text-white shadow-md flex-shrink-0">
        <div className="h-9 w-9 sm:h-10 sm:w-10 rounded-full flex items-center justify-center bg-white/20 hover:bg-white/30 transition flex-shrink-0">
          <Sparkles className="h-4 w-4 sm:h-5 sm:w-5 text-white" />
        </div>
        <span className="text-lg sm:text-xl font-semibold tracking-wide truncate">BizzAuto</span>
      </div>

      <nav className="flex-grow p-3 sm:p-4 space-y-2 bg-gradient-to-b from-blue-50 to-white dark:from-[#0f172a] dark:to-[#1e293b] transition-colors overflow-y-auto">
        {menuItems.map((item) => {
          const Icon = item.icon;
          const isActive = pathname === item.path;
          return (
            <Button
              key={item.name}
              variant="ghost"
              className={`w-full justify-start gap-2 sm:gap-3 rounded-lg text-sm sm:text-base font-medium transition-all duration-200 px-3 py-2 ${isActive ? "bg-blue-600 text-white shadow-sm hover:bg-blue-700" : "text-gray-700 dark:text-gray-200 hover:bg-blue-100 hover:text-blue-600 dark:hover:bg-blue-900/40 dark:hover:text-blue-400"}`}
              onClick={() => handleNavigation(item.path)}
            >
              <Icon className="h-4 w-4 sm:h-5 sm:w-5 flex-shrink-0" />
              <span className="truncate">{item.name}</span>
            </Button>
          );
        })}
      </nav>

      <div suppressHydrationWarning className="p-3 sm:p-4 mx-2 sm:mx-3 mb-4 sm:mb-5 rounded-2xl bg-gradient-to-br from-blue-100 via-white to-blue-50 border border-blue-200 shadow-md dark:from-[#0d1b2a] dark:via-[#1b263b] dark:to-[#0d1b2a] dark:border-blue-900/40 backdrop-blur-md transition-all duration-500 hover:shadow-lg hover:-translate-y-[2px]">
        <div className="rounded-xl p-2.5 sm:p-3 bg-white/60 dark:bg-[#0f172a]/70 shadow-inner transition-all flex items-center gap-2 sm:gap-3 mb-3 overflow-hidden">
          <Avatar className="h-9 w-9 sm:h-10 sm:w-10 ring-2 ring-blue-400 dark:ring-blue-600 shadow-sm flex-shrink-0">
            <AvatarFallback className="font-semibold text-black-900 dark:text-black-600">{avatarLetter}</AvatarFallback>
          </Avatar>
          <div className="flex-1 min-w-0 overflow-hidden">
            <p className="text-sm font-semibold text-gray-800 dark:text-gray-100 truncate">{userName}</p>
            <p className="text-xs text-gray-500 dark:text-gray-400 truncate break-all" title={userEmail}>{userEmail}</p>
          </div>
        </div>
        <Badge variant="secondary" className="text-[11px] bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300 px-2 py-1 rounded-md truncate max-w-full inline-block">{userRole}</Badge>

        <Button variant="ghost" className="w-full justify-start gap-2 mt-3 sm:mt-4 font-medium text-white bg-red-500 dark:bg-red-600 rounded-xl px-3 py-2 transition-all duration-300 hover:bg-gradient-to-r hover:from-red-600 hover:to-red-700 dark:hover:from-red-700 dark:hover:to-red-500 hover:text-white dark:hover:text-white shadow-md hover:shadow-lg active:scale-[0.98]" onClick={logout}>
          <LogOut className="h-4 w-4 sm:h-5 sm:w-5 flex-shrink-0" /> <span className="truncate">Sign Out</span>
        </Button>
      </div>
    </div>
  );
};

export default function Sidebar() {
  return (
    <aside className="hidden lg:flex w-64 flex-col fixed inset-y-0 bg-gradient-to-b from-blue-100 via-white to-blue-50 border-r border-blue-200 dark:from-[#0f172a] dark:via-[#1e293b] dark:to-[#1e3a8a]/30 dark:border-gray-800 shadow-md backdrop-blur-md transition-all">
      <NavigationContent />
    </aside>
  );
}