'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { apiClient } from '@/lib/api-client';
import { API_ENDPOINTS } from '@/lib/api-config';
import { FiClock, FiSend, FiList } from 'react-icons/fi';
import Sidebar, { NavigationContent } from "@/components/Sidebar";
import { Button } from "@/components/ui/button";
import { Sheet, SheetContent, SheetTrigger } from '@/components/ui/sheet';
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { Menu, Search, Bell, Sun, Moon } from 'lucide-react';
import { Input } from "@/components/ui/input";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { useTheme } from "@/hooks/use-theme";

// --- Type Definitions ---
type ScheduledMessage = {
  id: string;
  company_id: string;
  phone: string;
  message: string;
  scheduled_at: string;
  status: string;
};

type ApiResponse<T> = {
  data?: T;
  error?: string;
};

// --- Main Component ---
export default function WhatsappPage() {
  // --- State Management ---
  const router = useRouter();
  const { theme, toggleTheme, mounted } = useTheme();
  const [search, setSearch] = useState("");
  const [sheetOpen, setSheetOpen] = useState(false);

  // Send Message Form
  const [to, setTo] = useState('');
  const [body, setBody] = useState('');
  const [isSending, setIsSending] = useState(false);
  const [sendError, setSendError] = useState<string | null>(null);
  const [sendSuccess, setSendSuccess] = useState<string | null>(null);

  // Schedule Message Form
  const [scheduleTo, setScheduleTo] = useState('');
  const [scheduleBody, setScheduleBody] = useState('');
  const [scheduleDateTime, setScheduleDateTime] = useState('');
  const [isScheduling, setIsScheduling] = useState(false);
  const [scheduleError, setScheduleError] = useState<string | null>(null);
  const [scheduleSuccess, setScheduleSuccess] = useState<string | null>(null);

  // Scheduled Messages List
  const [scheduledMessages, setScheduledMessages] = useState<ScheduledMessage[]>([]);
  const [isLoadingMessages, setIsLoadingMessages] = useState(true);
  const [fetchMessagesError, setFetchMessagesError] = useState<string | null>(null);

  // --- API Calls ---

  // Fetch scheduled messages
  const fetchScheduledMessages = async () => {
    setIsLoadingMessages(true);
    setFetchMessagesError(null);
    try {
      const response = await apiClient.get<ScheduledMessage[]>(API_ENDPOINTS.scheduledWhatsappMessages);
      setScheduledMessages(response.data || []);
    } catch (err: any) {
      setFetchMessagesError(err.response?.data?.detail || err.message || "Failed to fetch scheduled messages.");
      console.error("Error fetching scheduled messages:", err);
    } finally {
      setIsLoadingMessages(false);
    }
  };

  // Send message immediately
  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSending(true);
    setSendError(null);
    setSendSuccess(null);
    try {
      const response = await apiClient.post(API_ENDPOINTS.sendMetaWhatsapp, { to, message_data: body });
      setSendSuccess('Message sent successfully!');
      setTo('');
      setBody('');
      fetchScheduledMessages();
    } catch (err: any) {
      setSendError(`An error occurred: ${err.response?.data?.detail || err.message}`);
      console.error("Error sending message:", err);
    } finally {
      setIsSending(false);
    }
  };

  // Schedule a new message
  const handleScheduleMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsScheduling(true);
    setScheduleError(null);
    setScheduleSuccess(null);
    try {
      const scheduled_at = new Date(scheduleDateTime).toISOString();
      const payload = {
        phone: scheduleTo,
        message: scheduleBody,
        scheduled_at,
      };
      const response = await apiClient.post(API_ENDPOINTS.scheduledWhatsappMessages, payload);
      setScheduleSuccess('Message sent successfully');
      setScheduleTo('');
      setScheduleBody('');
      setScheduleDateTime('');
      fetchScheduledMessages(); // Refresh the list
    } catch (err: any) {
      setScheduleError(`An error occurred: ${err.response?.data?.detail || err.message}`);
      console.error("Error scheduling message:", err);
    } finally {
      setIsScheduling(false);
    }
  };

  // --- Effects ---
  useEffect(() => {
    fetchScheduledMessages();
  }, []);

  // --- UI Rendering ---
  return (
    <div className="flex min-h-screen bg-background overflow-hidden">
      <Sidebar />

      <div className="flex-1 flex flex-col overflow-y-auto transition-all duration-300 lg:ml-64">
        <header className="border-b bg-card px-4 py-3 flex items-center justify-between sticky top-0 z-40">
          <div className="flex items-center gap-3 flex-1">
            <Sheet open={sheetOpen} onOpenChange={setSheetOpen}>
              <SheetTrigger asChild className="lg:hidden">
                <Button variant="outline" size="icon">
                  <Menu className="h-5 w-5" />
                </Button>
              </SheetTrigger>
              <SheetContent side="left" className="p-0 w-64">
                <NavigationContent setOpen={setSheetOpen} />
              </SheetContent>
            </Sheet>

            <div className="relative flex-1 max-w-full">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="pl-10 w-full bg-background border-border rounded-lg focus:ring-2 focus:ring-blue-500 transition-all duration-300"
              />
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Button variant="ghost" size="icon" className="relative hover:bg-muted transition">
              <Bell className="h-5 w-5" />
              <span className="absolute -top-1 -right-1 h-4 w-4 bg-destructive rounded-full text-[10px] text-white flex items-center justify-center">
                3
              </span>
            </Button>

            <Button variant="ghost" size="icon" onClick={toggleTheme}>
              {mounted && theme === "dark" ? <Sun className="h-5 w-5 text-yellow-400" /> : <Moon className="h-5 w-5 text-blue-500" />}
            </Button>

            <div onClick={() => router.push('/settings')} className="cursor-pointer hover:scale-105 transition-transform duration-200">
              <Avatar>
                <AvatarFallback className="bg-primary text-primary-foreground">{mounted ? localStorage.getItem("user_avatar")?.charAt(0).toUpperCase() || 'M' : 'M'}</AvatarFallback>
              </Avatar>
            </div>
          </div>
        </header>

        <main className="p-4 md:p-8 space-y-8">
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3">
            <div>
              <h1 className="text-xl md:text-2xl font-bold text-foreground">WhatsApp Messenger</h1>
              <p className="text-muted-foreground text-sm md:text-base">
                Send and schedule messages
              </p>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Send Message Card */}
            <div className="bg-card p-6 rounded-lg border border-border shadow-md">
              <h2 className="text-xl font-semibold mb-4 flex items-center text-foreground"><FiSend className="mr-2" /> Send a Message</h2>
              <form onSubmit={handleSendMessage} className="space-y-4">
                <div>
                  <label htmlFor="to" className="block text-sm font-medium text-foreground">To (with country code)</label>
                  <Input type="text" id="to" value={to} onChange={(e) => setTo(e.target.value)} placeholder="e.g., 923001234567" required className="mt-1" />
                </div>
                <div>
                  <label htmlFor="body" className="block text-sm font-medium text-foreground">Message</label>
                  <textarea id="body" value={body} onChange={(e) => setBody(e.target.value)} rows={4} required className="mt-1 w-full rounded-md border bg-background border-border shadow-sm focus:border-indigo-500 focus:ring-indigo-500" />
                </div>
                <Button type="submit" disabled={isSending} className="w-full bg-blue-600 text-white hover:bg-blue-700 disabled:bg-gray-400 flex items-center justify-center">
                  {isSending ? 'Sending...' : 'Send Now'}
                </Button>
                {sendSuccess && <p className="text-green-600 text-sm mt-2">{sendSuccess}</p>}
                {sendError && <p className="text-red-600 text-sm mt-2">{sendError}</p>}
              </form>
            </div>

            {/* Schedule Message Card */}
            <div className="bg-card p-6 rounded-lg border border-border shadow-md">
              <h2 className="text-xl font-semibold mb-4 flex items-center text-foreground"><FiClock className="mr-2" /> Schedule a Message</h2>
              <form onSubmit={handleScheduleMessage} className="space-y-4">
                <div>
                  <label htmlFor="scheduleTo" className="block text-sm font-medium text-foreground">To (with country code)</label>
                  <Input type="text" id="scheduleTo" value={scheduleTo} onChange={(e) => setScheduleTo(e.target.value)} placeholder="e.g., 923001234567" required className="mt-1" />
                </div>
                <div>
                  <label htmlFor="scheduleBody" className="block text-sm font-medium text-foreground">Message</label>
                  <textarea id="scheduleBody" value={scheduleBody} onChange={(e) => setScheduleBody(e.target.value)} rows={4} required className="mt-1 w-full rounded-md border bg-background border-border shadow-sm focus:border-indigo-500 focus:ring-indigo-500" />
                </div>
                <div>
                  <label htmlFor="scheduleDateTime" className="block text-sm font-medium text-foreground">Date and Time</label>
                  <Input type="datetime-local" id="scheduleDateTime" value={scheduleDateTime} onChange={(e) => setScheduleDateTime(e.target.value)} required className="mt-1" />
                </div>
                <Button type="submit" disabled={isScheduling} className="w-full bg-green-600 text-white hover:bg-green-700 disabled:bg-gray-400 flex items-center justify-center">
                  {isScheduling ? 'Scheduling...' : 'Schedule Message'}
                </Button>

                {scheduleSuccess && <p className="text-green-600 text-sm mt-2">{scheduleSuccess}</p>}

                {scheduleError && (
                  <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-md flex items-start animate-in fade-in slide-in-from-top-2 duration-300">
                    <div className="flex-shrink-0">
                      <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                      </svg>
                    </div>
                    <div className="ml-3">
                      <h3 className="text-sm font-medium text-red-800">Error</h3>
                      <div className="mt-1 text-sm text-red-700">
                        <p>{scheduleError}</p>
                      </div>
                    </div>
                  </div>
                )}
              </form>
            </div>
          </div>

          {/* Scheduled Messages List */}
          <div className="bg-card p-6 rounded-lg border border-border shadow-md">
            <h2 className="text-xl font-semibold mb-4 flex items-center text-foreground"><FiList className="mr-2" /> Scheduled Messages</h2>
            {isLoadingMessages ? (
              <p className="text-muted-foreground">Loading messages...</p>
            ) : fetchMessagesError ? (
              <p className="text-red-600">{fetchMessagesError}</p>
            ) : (
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-border">
                  <thead className="bg-muted">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">To</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">Message</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">Scheduled At</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">Status</th>
                    </tr>
                  </thead>
                  <tbody className="bg-card divide-y divide-border">
                    {scheduledMessages.length > 0 ? (
                      scheduledMessages.map((msg) => (
                        <tr key={msg.id}>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-foreground">{msg.phone}</td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-muted-foreground truncate max-w-xs">{msg.message}</td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-muted-foreground">
                            {new Date(msg.scheduled_at.endsWith('Z') ? msg.scheduled_at : msg.scheduled_at + 'Z').toLocaleString()}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm">
                            <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${msg.status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                              msg.status === 'sent' ? 'bg-green-100 text-green-800' :
                                'bg-red-100 text-red-800'
                              }`}>
                              {msg.status}
                            </span>
                          </td>
                        </tr>
                      ))
                    ) : (
                      <tr>
                        <td colSpan={4} className="px-6 py-4 text-center text-sm text-muted-foreground">No scheduled messages.</td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </main>
      </div>
    </div>
  );
}
