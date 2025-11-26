'use client';

import React, { useState } from 'react';
import { Input } from "@/components/ui/input";
import Sidebar, { NavigationContent } from '@/components/Sidebar';
import { Sheet, SheetContent, SheetTrigger, SheetHeader, SheetTitle, SheetDescription } from '@/components/ui/sheet';
import { Button } from '@/components/ui/button';
import { Search, Menu, Sun, Moon, Bell } from 'lucide-react';
import { useTheme } from '@/hooks/use-theme';
import { Avatar} from "@/components/ui/avatar";
import { AvatarFallback } from '@/components/ui/avatar';
import { DailyExpensesContent } from './Content';
import UserAvatar from '@/components/UserAvatar';


const DailyExpensesLayout: React.FC = () => {
  const { theme, toggleTheme } = useTheme();
  const [open, setOpen] = useState(false);
  const [mounted, setMounted] = useState(false);
  React.useEffect(() => { setMounted(true); }, []);

  return (
    <div className="flex min-h-screen bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-gray-900 dark:to-blue-900 overflow-hidden">
      {/* Sidebar - Hidden on mobile */}
      <div className="hidden lg:block">
        <Sidebar />
      </div>

  <div className="flex-1 flex flex-col transition-all duration-300 lg:ml-64">
  <header className="border-b bg-card px-2 sm:px-4 py-2 sm:py-3 flex items-center justify-between sticky top-0 z-40">
  <div className="flex items-center gap-3 flex-1 min-w-0">
    {/* Mobile Sidebar */}
    <Sheet open={open} onOpenChange={setOpen}>
      <SheetTrigger asChild className="lg:hidden">
        <Button variant="outline" size="icon">
          <Menu className="h-5 w-5" />
        </Button>
      </SheetTrigger>
      <SheetContent side="left" className="p-0 w-64">
        <SheetHeader className="px-4 py-2 border-b dark:border-gray-800">
          <SheetTitle>Dashboard Navigation</SheetTitle>
        </SheetHeader>
               <NavigationContent setOpen={setOpen} />
      </SheetContent>
    </Sheet>

    {/* Search Bar (Full Stretch) */}
    <div className="relative flex-1 max-w-full min-w-0">
      <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
      <Input
        placeholder="Search anything..."
        className="pl-10 w-full min-w-0 bg-background border border-gray-200 dark:border-gray-700 rounded-lg focus:ring-2 focus:ring-blue-500 transition-all duration-300 text-sm placeholder:text-sm"
      />
    </div>
  </div>

<div className="flex items-center gap-0 ml-1 mr-2 pr-2 flex-shrink-0">

  <Button
    variant="ghost"
    size="icon"
    className="relative hover:bg-blue-50 dark:hover:bg-gray-800 transition p-[5px]"
  >
    <Bell className="h-4 w-4" />
    <span className="absolute -top-1 -right-1 h-3.5 w-3.5 bg-destructive rounded-full text-[9px] text-white flex items-center justify-center">
      3
    </span>
  </Button>

    <Button
    variant="ghost"
    size="icon"
    onClick={toggleTheme}
    className="hover:bg-blue-50 dark:hover:bg-gray-800 transition p-2 rounded"
  >
    {mounted ? (
      theme === "dark" ? (
        <Sun className="h-4 w-4 text-yellow-400" />
      ) : (
        <Moon className="h-4 w-4 text-blue-500" />
      )
    ) : null}
  </Button>

   <Avatar className="cursor-pointer hover:scale-105 transition-transform duration-200">
              <AvatarFallback className="bg-primary text-primary-foreground">{typeof window !== 'undefined' ? localStorage.getItem("user_avatar")?.charAt(0).toUpperCase() || 'M' : 'M'}</AvatarFallback>
            </Avatar>
</div>


</header>

        {/* Main Page Content */}
        <main className="flex-1 px-3 sm:px-4 md:px-6 lg:px-8 py-4 sm:py-6 overflow-y-auto bg-gradient-to-b from-transparent to-white/50 dark:to-gray-900/50">
          <div className="max-w-7xl mx-auto w-full space-y-4 sm:space-y-6 min-h-[calc(100vh-8rem)]">
            <DailyExpensesContent />
          </div>
        </main>

        {/* Footer */}
        <footer className="border-t border-blue-200/30 dark:border-blue-800/30 bg-white/80 dark:bg-gray-900/80 backdrop-blur-md px-4 py-4 text-center text-[13px] sm:text-sm text-blue-600/80 dark:text-blue-400/80 select-none">
          &copy; {new Date().getFullYear()} Your Company. All rights reserved.
        </footer>
      </div>
    </div>
  );
};

export default DailyExpensesLayout;
