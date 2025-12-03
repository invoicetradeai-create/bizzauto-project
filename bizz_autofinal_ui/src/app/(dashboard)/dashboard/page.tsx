
"use client";

import { useState, useEffect } from "react";
import { useTheme } from "@/hooks/use-theme";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import {
  Sheet,
  SheetContent,
  SheetTrigger,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import {
  Users, DollarSign, Clock, Box, MessageSquare, FileText,
  UserPlus, Send, FileBarChart, Bell, Search, Sun, Moon, Menu
} from "lucide-react";
import {
  LineChart, Line, PieChart, Pie, Cell, ResponsiveContainer, XAxis, YAxis, Tooltip
} from "recharts";
import Sidebar, { NavigationContent } from "@/components/Sidebar";
import { apiClient } from "@/lib/api-client";

// Define the structure of the summary data from the backend
interface DashboardSummary {
  stats: {
    total_revenue: number;
    pending_payments: number;
    active_clients: number;
    low_stock_items: number;
    messages_sent: number;
  };
  revenue_trend: { month: string; value: number }[];
  payment_status: { name: string; value: number }[];
}

const PIE_CHART_COLORS = ["#10B981", "#F59E0B", "#EF4444", "#6B7280"];

const Dashboard = () => {
  const router = useRouter();
  const { theme, toggleTheme, mounted } = useTheme();
  const [open, setOpen] = useState(false);
  const [greeting, setGreeting] = useState("");
  const [emoji, setEmoji] = useState("");

  useEffect(() => {
    const getDynamicGreeting = () => {
      const currentHour = new Date().getHours();
      if (currentHour >= 5 && currentHour < 12) {
        setGreeting("Good Morning");
        setEmoji("👋");
      } else if (currentHour >= 12 && currentHour < 17) { // 12 PM to 4:59 PM
        setGreeting("Good Afternoon");
        setEmoji("☀️");
      } else if (currentHour >= 17 && currentHour < 21) { // 5 PM to 8:59 PM
        setGreeting("Good Evening");
        setEmoji("🌙");
      } else { // 9 PM to 4:59 AM
        setGreeting("Good Night");
        setEmoji("😴");
      }
    };

    getDynamicGreeting();
    // Re-evaluate greeting if the component remains mounted across time boundaries
    const interval = setInterval(getDynamicGreeting, 60 * 60 * 1000); // Check every hour
    return () => clearInterval(interval);
  }, []);

  // State for backend data
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setError(null);
      try {
        const response = await apiClient.get<DashboardSummary>('/dashboard/summary');
        setSummary(response.data);
      } catch (err: any) {
        setError(err.response?.data?.detail || err.message || "Failed to fetch dashboard summary");
        console.error("Error fetching dashboard summary:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  // Format numbers as currency
  const formatCurrency = (value: number) => 
    new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'PKR', minimumFractionDigits: 0 }).format(value);

  const statsCards = [
    { title: "Total Revenue", value: summary ? formatCurrency(summary.stats.total_revenue) : "...", icon: <DollarSign className="h-5 w-5 text-blue-500" /> },
    { title: "Pending Payments", value: summary ? formatCurrency(summary.stats.pending_payments) : "...", icon: <Clock className="h-5 w-5 text-blue-500" /> },
    { title: "Active Clients", value: summary ? summary.stats.active_clients : "...", icon: <Users className="h-5 w-5 text-blue-500" /> },
    { title: "Low Stock Items", value: summary ? summary.stats.low_stock_items : "...", icon: <Box className="h-5 w-5 text-blue-500" /> },
    { title: "Messages Sent", value: summary ? summary.stats.messages_sent : "...", icon: <MessageSquare className="h-5 w-5 text-blue-500" /> },
  ];

  return (
    <div className="flex min-h-screen bg-background overflow-hidden">
      <Sidebar />

      <div className="flex-1 flex flex-col transition-all duration-300 lg:ml-64">
        <header className="border-b bg-card px-4 py-3 flex items-center justify-between sticky top-0 z-40">
          <div className="flex items-center gap-3 flex-1">
            <Sheet open={open} onOpenChange={setOpen}><SheetTrigger asChild className="lg:hidden"><Button variant="outline" size="icon"><Menu className="h-5 w-5" /></Button></SheetTrigger><SheetContent side="left" className="p-0 w-64"><SheetHeader className="px-4 py-2 border-b dark:border-gray-800"><SheetTitle>Dashboard Navigation</SheetTitle></SheetHeader><NavigationContent setOpen={setOpen} /></SheetContent></Sheet>
            <div className="relative flex-1 max-w-full"><Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" /><Input placeholder="Search anything..." className="pl-10 w-full bg-background border border-gray-200 dark:border-gray-700 rounded-lg focus:ring-2 focus:ring-blue-500 transition-all duration-300" /></div>
          </div>
          <div className="flex items-center gap-[0px] sm:gap-[1px] md:gap-[2px] ml-[1px]">
            <Button variant="ghost" size="icon" className="relative hover:bg-blue-50 dark:hover:bg-gray-800 transition p-[5px]"><Bell className="h-4 w-4" /><span className="absolute -top-1 -right-1 h-3.5 w-3.5 bg-destructive rounded-full text-[9px] text-white flex items-center justify-center">3</span></Button>
            <Button variant="ghost" size="icon" onClick={toggleTheme} className="hover:bg-blue-50 dark:hover:bg-gray-800 transition p-[5px]">{mounted && theme === "dark" ? <Sun className="h-4 w-4 text-yellow-400" /> : <Moon className="h-4 w-4 text-blue-500" />}</Button>
            <div onClick={() => router.push('/settings')} className="cursor-pointer hover:scale-105 transition-transform duration-200 ml-[1px]">
              <Avatar>
                <AvatarFallback className="bg-primary text-primary-foreground text-[13px]">{mounted ? localStorage.getItem("user_avatar")?.charAt(0).toUpperCase() || 'M' : 'M'}</AvatarFallback>
              </Avatar>
            </div>
          </div>
        </header>

        <main className="flex-1 p-4 md:p-6 overflow-y-auto">
          {loading ? (
            <div className="text-center">Loading dashboard...</div>
          ) : error ? (
            <div className="text-center text-destructive">Error: {error}</div>
          ) : summary && (
            <>
              <div className="mb-6 p-6 md:p-8 rounded-xl bg-gradient-to-r from-blue-500 via-purple-500 to-teal-500 text-white text-center md:text-left">
                <h1 className="text-2xl md:text-4xl font-bold mb-2">{greeting}! {emoji}</h1>
                <p className="text-sm md:text-lg opacity-90">Welcome back! Here's your business overview for today.</p>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
                {[ { title: "Create Invoice", path: "/invoices", color: "bg-blue-500 hover:bg-blue-600", icon: <FileText className="h-6 w-6" />, desc: "Generate new invoice" }, { title: "Add Client", path: "/crm", color: "bg-purple-500 hover:bg-purple-600", icon: <UserPlus className="h-6 w-6" />, desc: "Register new client" }, { title: "Send WhatsApp", path: "/whatsapp", color: "bg-green-500 hover:bg-green-600", icon: <Send className="h-6 w-6" />, desc: "Message customers" }, { title: "View Reports", path: "/analytics", color: "bg-orange-500 hover:bg-orange-600", icon: <FileBarChart className="h-6 w-6" />, desc: "Business analytics" }, ].map((item, i) => ( <Card key={i} className={`${item.color} text-white border-0 cursor-pointer transition-colors`} onClick={() => router.push(item.path)}><CardContent className="p-5 md:p-6"><div className="flex items-start justify-between mb-4"><div className="h-12 w-12 rounded-lg bg-white/20 flex items-center justify-center">{item.icon}</div></div><h3 className="text-lg md:text-xl font-bold mb-1">{item.title}</h3><p className="text-sm opacity-90">{item.desc}</p></CardContent></Card> ))}
              </div>

              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4 mb-6">
                {statsCards.map((stat, i) => (
                  <Card key={i}><CardContent className="p-4 md:p-6"><div className="flex items-center justify-between mb-2"><p className="text-xs md:text-sm text-muted-foreground">{stat.title}</p>{stat.icon}</div><p className="text-lg md:text-2xl font-bold mb-1">{stat.value}</p></CardContent></Card>
                ))}
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
                <Card>
                  <CardHeader><CardTitle>Revenue Trend</CardTitle></CardHeader>
                  <CardContent>
                    <ResponsiveContainer width="100%" height={250}>
                      <LineChart data={summary.revenue_trend}><XAxis dataKey="month" stroke="#999" /><YAxis stroke="#999" /><Tooltip contentStyle={{ backgroundColor: theme === "dark" ? "#1f2937" : "#fff", border: "1px solid hsl(var(--border))", borderRadius: "8px" }} /><defs><linearGradient id="lineGradient" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor={theme === "dark" ? "#3b82f6" : "#2563eb"} stopOpacity={0.4} /><stop offset="100%" stopColor={theme === "dark" ? "#3b82f6" : "#2563eb"} stopOpacity={0} /></linearGradient></defs><Line type="monotone" dataKey="value" stroke={theme === "dark" ? "#3b82f6" : "#2563eb"} strokeWidth={2.5} fill="url(#lineGradient)" dot={{ fill: theme === "dark" ? "#3b82f6" : "#2563eb", stroke: theme === "dark" ? "#1f2937" : "#fff", strokeWidth: 1.5, r: 4 }} activeDot={{ fill: theme === "dark" ? "#60a5fa" : "#1d4ed8", r: 6 }} /></LineChart>
                    </ResponsiveContainer>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader><CardTitle>Payment Status</CardTitle></CardHeader>
                  <CardContent className="flex flex-col sm:flex-row items-center justify-center gap-6">
                    <ResponsiveContainer width={220} height={220}>
                      <PieChart>
                        <Pie data={summary.payment_status} cx="50%" cy="50%" innerRadius={60} outerRadius={90} paddingAngle={2} dataKey="value">
                          {summary.payment_status.map((entry, index) => ( <Cell key={`cell-${index}`} fill={PIE_CHART_COLORS[index % PIE_CHART_COLORS.length]} /> ))}
                        </Pie>
                      </PieChart>
                    </ResponsiveContainer>
                    <div className="space-y-2 text-sm">
                      {summary.payment_status.map((p, i) => ( <div key={i} className="flex items-center gap-2"><div className="h-3 w-3 rounded-full" style={{ backgroundColor: PIE_CHART_COLORS[i % PIE_CHART_COLORS.length] }} /><span>{p.name} ({p.value})</span></div> ))}
                    </div>
                  </CardContent>
                </Card>
              </div>
            </>
          )}
        </main>
      </div>
    </div>
  );
};

export default Dashboard;