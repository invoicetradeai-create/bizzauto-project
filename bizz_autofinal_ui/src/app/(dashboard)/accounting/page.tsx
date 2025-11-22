"use client";

import { useState, useEffect } from "react";
import { useTheme } from "@/hooks/use-theme";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Table, TableHeader, TableRow, TableHead, TableBody, TableCell } from "@/components/ui/table";
import { apiClient } from "@/lib/api-client";
import { API_ENDPOINTS } from "@/lib/api-config";
import { Plus, Printer, Moon, Sun, Search, Bell, Menu } from "lucide-react";
import Sidebar, { NavigationContent } from "@/components/Sidebar";
import { Input } from "@/components/ui/input";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Sheet, SheetContent, SheetTrigger, SheetHeader, SheetTitle } from "@/components/ui/sheet";

interface SalesSummary {
  id: string;
  company_id: string;
  client_id: string;
  invoice_date: string;
  total_amount: number;
  payment_status: string;
  notes: string;
}

interface ExpenseReport {
  category: string;
  sum: number;
}

interface StockReport {
  id: string;
  company_id: string;
  name: string;
  sku: string;
  category: string;
  purchase_price: number;
  sale_price: number;
  stock_quantity: number;
  low_stock_alert: number;
  unit: string;
}

export default function AccountingPage() {
  const { theme, toggleTheme } = useTheme();
  const [search, setSearch] = useState("");
  const [open, setOpen] = useState(false);
  const [salesSummary, setSalesSummary] = useState<SalesSummary[]>([]);
  const [expenseReport, setExpenseReport] = useState<ExpenseReport[]>([]);
  const [stockReport, setStockReport] = useState<StockReport[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchReports();
  }, []);

  const fetchReports = async () => {
    try {
      setLoading(true);
      const sales = await apiClient.get(API_ENDPOINTS.accounting.sales_summary);
      setSalesSummary(sales.data);

      const expenses = await apiClient.get(API_ENDPOINTS.accounting.expense_report);
      setExpenseReport(expenses.data);

      const stock = await apiClient.get(API_ENDPOINTS.accounting.stock_report);
      setStockReport(stock.data);
    } catch (err) {
      setError("Failed to fetch reports.");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const filteredSalesSummary = salesSummary.filter(
    (sale) =>
      sale.client_id.toLowerCase().includes(search.toLowerCase()) ||
      sale.payment_status.toLowerCase().includes(search.toLowerCase())
  );

  const filteredExpenseReport = expenseReport.filter((expense) =>
    expense.category.toLowerCase().includes(search.toLowerCase())
  );

  const filteredStockReport = stockReport.filter(
    (product) =>
      product.name.toLowerCase().includes(search.toLowerCase()) ||
      (product.sku && product.sku.toLowerCase().includes(search.toLowerCase()))
  );

  if (loading) {
    return <div className="flex justify-center items-center min-h-screen text-gray-600">Loading reports...</div>;
  }

  if (error) {
    return <div className="text-red-600 text-center mt-10">❌ Error loading reports: {error}</div>;
  }

  return (
    <div className="flex min-h-screen bg-background overflow-hidden">
      <Sidebar />

      <div className="flex-1 flex flex-col overflow-y-auto transition-all duration-300 lg:ml-64">
        <header className="border-b bg-card px-4 py-3 flex items-center justify-between sticky top-0 z-40">
          <div className="flex items-center gap-3 flex-1">
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

            <div className="relative flex-1 max-w-full">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search reports..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="pl-10 w-full bg-background border border-gray-200 dark:border-gray-700 rounded-lg focus:ring-2 focus:ring-blue-500 transition-all duration-300"
              />
            </div>
          </div>

          <div className="flex items-center gap-2">
            <Button variant="ghost" size="icon" className="relative hover:bg-blue-50 dark:hover:bg-gray-800 transition">
              <Bell className="h-5 w-5" />
              <span className="absolute -top-1 -right-1 h-4 w-4 bg-destructive rounded-full text-[10px] text-white flex items-center justify-center">
                3
              </span>
            </Button>

            <Button variant="ghost" size="icon" onClick={toggleTheme}>
              {theme === "dark" ? <Sun className="h-5 w-5 text-yellow-400" /> : <Moon className="h-5 w-5 text-blue-500" />}
            </Button>

            <Avatar className="cursor-pointer hover:scale-105 transition-transform duration-200">
              <AvatarFallback className="bg-primary text-primary-foreground">{typeof window !== 'undefined' ? localStorage.getItem("user_avatar")?.charAt(0).toUpperCase() || 'M' : 'M'}</AvatarFallback>
            </Avatar>
          </div>
        </header>

        <div className="p-4 md:p-6 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3">
          <div>
            <h1 className="text-xl md:text-2xl font-bold">Accounting Reports</h1>
            <p className="text-muted-foreground text-sm md:text-base">
              View your sales, expenses, and stock reports
            </p>
          </div>
          <div className="flex gap-2">
            <Button>
              <Plus className="w-4 h-4 mr-2" />
              Export
            </Button>
            <Button>
              <Printer className="w-4 h-4 mr-2" />
              Print
            </Button>
          </div>
        </div>

        <div className="px-4 md:px-6 pb-6">
          <Tabs defaultValue="sales_summary">
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="sales_summary">Sales Summary</TabsTrigger>
              <TabsTrigger value="expense_report">Expense Report</TabsTrigger>
              <TabsTrigger value="stock_report">Stock Report</TabsTrigger>
            </TabsList>
            <TabsContent value="sales_summary" className="mt-4">
              <Card>
                <CardHeader>
                  <CardTitle>Sales Summary</CardTitle>
                </CardHeader>
                <CardContent>
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Invoice ID</TableHead>
                        <TableHead>Client ID</TableHead>
                        <TableHead>Date</TableHead>
                        <TableHead>Amount</TableHead>
                        <TableHead>Status</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {filteredSalesSummary.map((sale) => (
                        <TableRow key={sale.id}>
                          <TableCell>{sale.id}</TableCell>
                          <TableCell>{sale.client_id}</TableCell>
                          <TableCell>{new Date(sale.invoice_date).toLocaleDateString()}</TableCell>
                          <TableCell>${sale.total_amount.toFixed(2)}</TableCell>
                          <TableCell>{sale.payment_status}</TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </CardContent>
              </Card>
            </TabsContent>
            <TabsContent value="expense_report" className="mt-4">
              <Card>
                <CardHeader>
                  <CardTitle>Expense Report</CardTitle>
                </CardHeader>
                <CardContent>
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Category</TableHead>
                        <TableHead>Total Amount</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {filteredExpenseReport.map((expense) => (
                        <TableRow key={expense.category}>
                          <TableCell>{expense.category}</TableCell>
                          <TableCell>${expense.sum.toFixed(2)}</TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </CardContent>
              </Card>
            </TabsContent>
            <TabsContent value="stock_report" className="mt-4">
              <Card>
                <CardHeader>
                  <CardTitle>Stock Report</CardTitle>
                </CardHeader>
                <CardContent>
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Product Name</TableHead>
                        <TableHead>SKU</TableHead>
                        <TableHead>Category</TableHead>
                        <TableHead>Stock Quantity</TableHead>
                        <TableHead>Sale Price</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {filteredStockReport.map((product) => (
                        <TableRow key={product.id}>
                          <TableCell>{product.name}</TableCell>
                          <TableCell>{product.sku}</TableCell>
                          <TableCell>{product.category}</TableCell>
                          <TableCell>{product.stock_quantity}</TableCell>
                          <TableCell>${product.sale_price.toFixed(2)}</TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </div>
      </div>
    </div>
  );
}
