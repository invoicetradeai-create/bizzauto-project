"use client";

import { useState, useEffect, useMemo } from "react";
import { useTheme } from "@/hooks/use-theme";
import { Button } from "@/components/ui/button";
import { Moon, Sun, Bell, Menu, Search } from "lucide-react";
import Sidebar, { NavigationContent } from "@/components/Sidebar";
import { Input } from "@/components/ui/input";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Sheet, SheetContent, SheetTrigger, SheetHeader, SheetTitle } from "@/components/ui/sheet";
import {
  DollarSign,
  Users,
  Package,
  MessageSquare,
} from "lucide-react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  BarChart,
  Bar,
  ResponsiveContainer,
  Legend,
} from "recharts";


// import { Invoice, Client, Product, WhatsappLog } from "@/bizzauto_api/models"; // Adjust path as needed

import { format } from "date-fns";
import { Invoice, Client, Product, WhatsappLog } from "../../../../types";
import { API_ENDPOINTS } from "@/lib/api-config";
import { apiClient } from "@/lib/api-client";

export default function AnalyticsPage() {
  const { theme, toggleTheme } = useTheme();
  const [activeTab, setActiveTab] = useState("Revenue");
  const [open, setOpen] = useState(false);

  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [clients, setClients] = useState<Client[]>([]);
  const [products, setProducts] = useState<Product[]>([]);
  const [whatsappLogs, setWhatsappLogs] = useState<WhatsappLog[]>([]);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const [
          invoicesRes,
          clientsRes,
          productsRes,
          whatsappLogsRes,
        ] = await Promise.all([
          apiClient.get<Invoice[]>(API_ENDPOINTS.invoices),
          apiClient.get<Client[]>(API_ENDPOINTS.clients),
          apiClient.get<Product[]>(API_ENDPOINTS.products),
          // apiClient.get<WhatsappLog[]>(API_ENDPOINTS.whatsappLogs), // This endpoint does not exist
        ]);

        if (invoicesRes.data) setInvoices(invoicesRes.data);
        if (clientsRes.data) setClients(clientsRes.data);
        if (productsRes.data) setProducts(productsRes.data);
        // if (whatsappLogsRes.data) setWhatsappLogs(whatsappLogsRes.data);

      } catch (err) {
        setError("Failed to fetch analytics data.");
        console.error("Error fetching analytics data:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  // Process data for charts and stats
  const { revenueData, clientData, productData, messageData, stats } = useMemo(() => {
    const currentYear = new Date().getFullYear();
    const monthlyRevenue: { [key: string]: number } = {};
    const monthlyClients: { [key: string]: Set<string> } = {}; // Use Set to count unique clients
    const productSales: { [key: string]: number } = {};
    const dailyMessages: { [key: string]: { sent: number; received: number } } = {};

    // Initialize for current year
    for (let i = 0; i < 12; i++) {
      const month = format(new Date(currentYear, i, 1), "MMM");
      monthlyRevenue[month] = 0;
      monthlyClients[month] = new Set();
    }

    // Process Invoices for Revenue
    invoices.forEach(invoice => {
      const invoiceDate = new Date(invoice.invoice_date);
      if (invoiceDate.getFullYear() === currentYear) {
        const month = format(invoiceDate, "MMM");
        monthlyRevenue[month] += invoice.total_amount || 0;
      }
    });

    // Process Clients for Client Growth (simplified: count active clients per month)
    clients.forEach(client => {
        // This is a simplification. A more accurate client growth would track when a client was added.
        // For now, we'll just count total clients.
    });

    // Process Products (assuming products array contains all products, not sales data)
    // To get product sales, we'd need invoice_items or a dedicated sales endpoint.
    // For now, we'll just count total products.
    // If productData is meant to be sales, we need to fetch invoice_items.
    // Let's assume productData is for product count for now.
    
    // Process Whatsapp Logs for Message Activity
    whatsappLogs.forEach(log => {
      const logDate = new Date(log.created_at || new Date()); // Assuming created_at exists or use current date
      if (logDate.getFullYear() === currentYear) {
        const day = format(logDate, "EEE"); // Mon, Tue, etc.
        if (!dailyMessages[day]) {
          dailyMessages[day] = { sent: 0, received: 0 };
        }
        // Assuming all logs are 'sent' for simplicity, adjust if 'received' status exists
        dailyMessages[day].sent += 1; 
      }
    });


    const processedRevenueData = Object.keys(monthlyRevenue).map(month => ({
      month,
      revenue: monthlyRevenue[month],
      profit: monthlyRevenue[month] * 0.2, // Simplified profit calculation
    }));

    const processedClientData = Object.keys(monthlyClients).map(month => ({
        month,
        clients: monthlyClients[month].size,
    }));

    // Placeholder for productData until invoice_items are fetched or a better source is identified
    const processedProductData = products.map(p => ({
        name: p.name,
        sales: Math.floor(Math.random() * 5000) + 1000 // Placeholder sales
    }));

    const processedMessageData = Object.keys(dailyMessages).map(day => ({
        day,
        sent: dailyMessages[day].sent,
        received: dailyMessages[day].received, // Placeholder for received
    }));

    // Stats calculations
    const totalRevenue = invoices.reduce((sum, inv) => sum + (inv.total_amount || 0), 0);
    const totalClients = clients.length;
    const totalProductsSold = invoices.reduce((sum, inv) => sum + (inv.items?.length || 0), 0); // Simplified: count invoice items
    const totalMessagesSent = whatsappLogs.length;

    return {
      revenueData: processedRevenueData,
      clientData: processedClientData,
      productData: processedProductData,
      messageData: processedMessageData,
      stats: {
        totalRevenue: totalRevenue,
        totalClients: totalClients,
        totalProductsSold: totalProductsSold,
        totalMessagesSent: totalMessagesSent,
      },
    };
  }, [invoices, clients, products, whatsappLogs]);

  if (loading) {
    return <div className="flex min-h-screen items-center justify-center">Loading analytics...</div>;
  }

  if (error) {
    return <div className="flex min-h-screen items-center justify-center text-red-500">{error}</div>;
  }

  return (
    <div className="flex min-h-screen bg-background">
      {/* Sidebar */}
      <Sidebar />


      <div className="flex-1 flex flex-col transition-all duration-300 lg:ml-64">
      <header className="border-b bg-card px-4 py-3 flex items-center justify-between sticky top-0 z-40">
  <div className="flex items-center gap-3 flex-1">
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
    <div className="relative flex-1 max-w-full">
      <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
      <Input
        placeholder="Search anything..."
        className="pl-10 w-full bg-background border border-gray-200 dark:border-gray-700 rounded-lg focus:ring-2 focus:ring-blue-500 transition-all duration-300"
      />
    </div>
  </div>

<div className="flex items-center gap-[0px] sm:gap-[1px] md:gap-[2px] ml-[1px]">
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
    className="hover:bg-blue-50 dark:hover:bg-gray-800 transition p-[5px]"
  >
    {theme === "dark" ? (
      <Sun className="h-4 w-4 text-yellow-400" />
    ) : (
      <Moon className="h-4 w-4 text-blue-500" />
    )}
  </Button>

  <Avatar className="cursor-pointer hover:scale-105 transition-transform duration-200 ml-[1px]">
    <AvatarFallback className="bg-primary text-primary-foreground text-[13px]">
      {typeof window !== 'undefined' ? localStorage.getItem("user_avatar")?.charAt(0).toUpperCase() || 'M' : 'M'}
    </AvatarFallback>
  </Avatar>
</div>


</header>

        {/* Analytics Content */}
        <div className="p-4 sm:p-6 overflow-x-hidden">
          <h1 className="text-xl sm:text-2xl font-bold">Analytics & Reports</h1>
          <p className="text-muted-foreground mb-6 text-sm sm:text-base">
            Comprehensive business insights and performance metrics
          </p>

          {/* Stats Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6 mb-6">
            {[
              {
                label: "Total Revenue",
                value: `Rs ${stats.totalRevenue.toLocaleString()}`,
                icon: DollarSign,
                change: "+12.5%", // Placeholder, needs actual calculation
                color: "text-blue-600",
              },
              {
                label: "Client Growth",
                value: `+${stats.totalClients}`,
                icon: Users,
                change: "+18.2%", // Placeholder, needs actual calculation
                color: "text-green-600",
              },
              {
                label: "Products Sold",
                value: stats.totalProductsSold.toLocaleString(),
                icon: Package,
                change: "+8.3%", // Placeholder, needs actual calculation
                color: "text-purple-600",
              },
              {
                label: "Messages Sent",
                value: stats.totalMessagesSent.toLocaleString(),
                icon: MessageSquare,
                change: "-5.4%", // Placeholder, needs actual calculation
                color: "text-orange-500",
              },
            ].map((item, idx) => (
              <div
                key={idx}
                className="bg-card border-border border rounded-lg p-4 hover:shadow-sm transition"
              >
                <div className="flex items-center justify-between mb-2">
                  <p className="text-muted-foreground text-sm">{item.label}</p>
                  <item.icon className={`w-5 h-5 ${item.color}`} />
                </div>
                <h2 className="text-2xl font-semibold">{item.value}</h2>
                <p
                  className={`text-sm mt-1 ${
                    item.change.startsWith("+")
                      ? "text-green-600"
                      : "text-red-500"
                  }`}
                >
                  {item.change}
                </p>
              </div>
            ))}
          </div>

          {/* Tabs */}
<div className="flex gap-2 sm:gap-4 mb-6 w-full overflow-x-auto whitespace-nowrap no-scrollbar">
  {["Revenue", "Clients", "Products", "Messages"].map((tab) => (
    <button
      key={tab}
      onClick={() => setActiveTab(tab)}
      className={`px-4 py-2 rounded-full shadow text-sm font-medium flex-shrink-0 ${
        activeTab === tab
          ? "bg-blue-600 text-white border border-blue-600"
          : "bg-white text-gray-700 hover:bg-gray-100 dark:bg-gray-800 dark:text-gray-300 dark:hover:bg-gray-700"
      }`}
    >
      {tab}
    </button>
  ))}
</div>


          {/* ==================== TAB CONTENT ==================== */}

          {/* REVENUE TAB */}
          {activeTab === "Revenue" && (
            <div className="bg-card border-border border rounded-lg p-4 sm:p-6">
              <h2 className="text-foreground font-semibold mb-4">
                Revenue & Profit Trends
              </h2>
              <div className="h-[320px]">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={revenueData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#eee" />
                    <XAxis dataKey="month" stroke="#999" />
                    <YAxis stroke="#999" />
                    <Tooltip />
                    <Legend />
                    <Line
                      type="monotone"
                      dataKey="revenue"
                      stroke="#3b82f6"
                      strokeWidth={2}
                      dot={{ r: 4 }}
                    />
                    <Line
                      type="monotone"
                      dataKey="profit"
                      stroke="#10b981"
                      strokeWidth={2}
                      dot={{ r: 4 }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>
          )}

          {/* CLIENTS TAB */}
          {activeTab === "Clients" && (
            <div className="bg-card border-border border rounded-lg p-4 sm:p-6">
              <h2 className="text-foreground font-semibold mb-4">
                Client Growth Over Time
              </h2>

              <div className="h-[320px]">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart
                    data={clientData}
                    margin={{ top: 10, right: 30, left: 0, bottom: 0 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" stroke="#eee" />
                    <XAxis dataKey="month" stroke="#999" />
                    <YAxis stroke="#999" />
                    <Tooltip />
                    <Legend />
                    <Line
                      type="monotone"
                      dataKey="clients"
                      stroke="#10b981"
                      strokeWidth={3}
                      dot={{ r: 5, stroke: "#10b981", strokeWidth: 2, fill: "#10b981" }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>
          )}

          {/* PRODUCTS TAB */}
          {activeTab === "Products" && (
            <div className="bg-card border-border border rounded-lg p-4 sm:p-6">
              <h2 className="text-foreground font-semibold mb-4">
                Product Performance
              </h2>
              <div className="h-[320px]">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={productData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#eee" />
                    <XAxis dataKey="name" stroke="#999" />
                    <YAxis stroke="#999" />
                    <Tooltip />
                    <Bar dataKey="sales" fill="#3b82f6" radius={[8, 8, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          )}

          {/* MESSAGES TAB */}
          {activeTab === "Messages" && (
            <div className="bg-card border rounded-lg p-4 sm:p-6">
              <h2 className="text-foreground font-semibold mb-4">
                Message Activity
              </h2>
              <div className="h-[320px]">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={messageData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#eee" />
                    <XAxis dataKey="day" stroke="#999" />
                    <YAxis stroke="#999" />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="sent" fill="#3b82f6" radius={[6, 6, 0, 0]} />
                    <Bar dataKey="received" fill="#10b981" radius={[6, 6, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}