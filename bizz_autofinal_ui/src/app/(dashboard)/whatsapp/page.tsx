"use client";

import { useState, useEffect } from "react";
import { useTheme } from "@/hooks/use-theme";
import { Button } from "@/components/ui/button";
import { Moon, Sun, Bell, Menu, Search, MessageCircle, Users, Clock, X } from "lucide-react";
import Sidebar, { NavigationContent } from "@/components/Sidebar";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Sheet, SheetContent, SheetTrigger, SheetHeader, SheetTitle } from "@/components/ui/sheet";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Card } from "@/components/ui/card";
import { apiClient } from "@/lib/api-client";
import DatePicker from 'react-datepicker';
import { useToast } from "@/hooks/use-toast";
import 'react-datepicker/dist/react-datepicker.css';

// Types
type ClientContact = { id: string; name: string; phone: string; };
type WhatsAppLog = { id: string; };
type Stats = { messagesSent: number; activeContacts: number; scheduled: number; };

// Schedule Modal Component
const ScheduleMessageModal = ({ contacts, onSchedule, onCancel }: { contacts: ClientContact[], onSchedule: (payload: any) => void, onCancel: () => void }) => {
  const [message, setMessage] = useState('');
  const [selectedContactId, setSelectedContactId] = useState<string>('');
  const [scheduledAt, setScheduledAt] = useState(new Date());

  const handleSave = () => {
    if (!selectedContactId || !message) {
      alert("Please select a contact and enter a message.");
      return;
    }
    const contact = contacts.find(c => c.id === selectedContactId);
    if (!contact) {
      alert("Selected contact not found.");
      return;
    }
    onSchedule({
      recipient_phone: contact.phone,
      recipient_name: contact.name,
      message,
      scheduled_at: scheduledAt.toISOString(),
    });
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-60 flex items-center justify-center z-50 p-4">
      <Card className="w-full max-w-lg">
        <div className="p-6 space-y-4">
          <div className="flex justify-between items-center"><h3 className="text-lg font-semibold">Schedule a Message</h3><Button variant="ghost" size="icon" type="button" onClick={onCancel}><X className="h-4 w-4" /></Button></div>
          <div><label className="text-sm font-medium">Contact</label><Select onValueChange={setSelectedContactId}><SelectTrigger><SelectValue placeholder="Select a contact..." /></SelectTrigger><SelectContent>{contacts.map(c => <SelectItem key={c.id} value={c.id}>{c.name} ({c.phone})</SelectItem>)}</SelectContent></Select></div>
          <div><label className="text-sm font-medium">Message</label><Textarea value={message} onChange={(e) => setMessage(e.target.value)} placeholder="Type your message here..." /></div>
          <div><label className="text-sm font-medium">Schedule Date & Time</label><DatePicker selected={scheduledAt} onChange={(date) => setScheduledAt(date || new Date())} showTimeSelect timeFormat="HH:mm" dateFormat="MMMM d, yyyy h:mm aa" className="w-full h-9 border border-input rounded-md px-3 py-2 text-sm" /></div>
        </div>
        <div className="bg-muted/50 px-6 py-3 flex justify-end gap-2"><Button type="button" variant="outline" onClick={onCancel}>Cancel</Button><Button type="button" onClick={handleSave}>Schedule</Button></div>
      </Card>
    </div>
  );
};


export default function WhatsAppPage() {
  const { theme, toggleTheme } = useTheme();
  const [selectedContact, setSelectedContact] = useState<ClientContact | null>(null);
  const [open, setOpen] = useState(false);
  const [isScheduling, setIsScheduling] = useState(false);

  const [contacts, setContacts] = useState<ClientContact[]>([]);
  const [stats, setStats] = useState<Stats>({ messagesSent: 0, activeContacts: 0, scheduled: 0 });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // New state and handler for the chat functionality
  const [messageText, setMessageText] = useState("");
  const [isSending, setIsSending] = useState(false);
  const { toast } = useToast();

  const handleSendMessage = async () => {
    if (!selectedContact) {
      toast({ title: "Error", description: "Please select a contact first.", variant: "destructive" });
      return;
    }
    if (!messageText.trim()) {
      toast({ title: "Error", description: "Cannot send an empty message.", variant: "destructive" });
      return;
    }

    setIsSending(true);
    try {
      const response = await fetch('/api/send-meta-whatsapp', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ to: selectedContact.phone, body: messageText }),
      });

      const result = await response.json();

      if (response.ok) {
        toast({ title: "Success", description: "Message sent successfully!" });
        setMessageText(""); // Clear input on success
        fetchData(); // Refresh stats to reflect new message count
      } else {
        throw new Error(result.detail || "An unknown error occurred");
      }
    } catch (err) {
      const errorDetail = err instanceof Error ? err.message : String(err);
      toast({ title: "Failed to Send", description: errorDetail, variant: "destructive" });
    } finally {
      setIsSending(false);
    }
  };

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [clientsRes, logsRes, scheduledRes] = await Promise.all([
        apiClient.get<ClientContact[]>('/tables/clients/'),
        apiClient.get<WhatsAppLog[]>('/tables/whatsapp_logs/'),
        apiClient.get<any[]>('/tables/scheduled_messages/')
      ]);

      if (clientsRes.data) setContacts(clientsRes.data);
      setStats(prev => ({ 
        ...prev, 
        activeContacts: clientsRes.data?.length || 0,
        messagesSent: logsRes.data?.length || 0,
        scheduled: scheduledRes.data?.length || 0,
      }));

    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "An unknown error occurred";
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleScheduleMessage = async (payload: any) => {
    try {
      const companiesRes = await apiClient.get<{id: string}[]>('/tables/companies/');
      if (!companiesRes.data || companiesRes.data.length === 0) throw new Error("No companies found.");
      
      const fullPayload = { ...payload, company_id: companiesRes.data[0].id };
      
      const response = await apiClient.post('/tables/scheduled_messages/', fullPayload);
      if (response.error) throw new Error(response.error);

      alert("Message scheduled successfully!");
      setIsScheduling(false);
      fetchData(); // Refresh stats
    } catch (err) {
      alert("Failed to schedule message: " + (err instanceof Error ? err.message : String(err)));
    }
  };

  return (
    <div className="flex h-screen bg-background overflow-hidden">
      {isScheduling && <ScheduleMessageModal contacts={contacts} onCancel={() => setIsScheduling(false)} onSchedule={handleScheduleMessage} />}
      <Sidebar />

      <div className="flex-1 flex flex-col transition-all duration-300 lg:ml-64">
        <header className="border-b bg-card px-4 py-3 flex items-center justify-between sticky top-0 z-40">
          <div className="flex items-center gap-3 flex-1"><Sheet open={open} onOpenChange={setOpen}><SheetTrigger asChild className="lg:hidden"><Button variant="outline" size="icon"><Menu className="h-5 w-5" /></Button></SheetTrigger><SheetContent side="left" className="p-0 w-64"><SheetHeader className="px-4 py-2 border-b dark:border-gray-800"><SheetTitle>Dashboard Navigation</SheetTitle></SheetHeader><NavigationContent setOpen={setOpen} /></SheetContent></Sheet><div className="relative flex-1 max-w-full"><Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" /><Input placeholder="Search anything..." className="pl-10 w-full bg-background border border-gray-200 dark:border-gray-700 rounded-lg focus:ring-2 focus:ring-blue-500 transition-all duration-300" /></div></div>
          <div className="flex items-center gap-[0px] sm:gap-[1px] md:gap-[2px] ml-[1px]"><Button variant="ghost" size="icon" className="relative hover:bg-blue-50 dark:hover:bg-gray-800 transition p-[5px]"><Bell className="h-4 w-4" /><span className="absolute -top-1 -right-1 h-3.5 w-3.5 bg-destructive rounded-full text-[9px] text-white flex items-center justify-center">3</span></Button><Button variant="ghost" size="icon" onClick={toggleTheme} className="hover:bg-blue-50 dark:hover:bg-gray-800 transition p-[5px]">{theme === "dark" ? <Sun className="h-4 w-4 text-yellow-400" /> : <Moon className="h-4 w-4 text-blue-500" />}</Button><Avatar className="cursor-pointer hover:scale-105 transition-transform duration-200 ml-[1px]"><AvatarFallback className="bg-primary text-primary-foreground text-[13px]">{typeof window !== 'undefined' ? localStorage.getItem("user_avatar")?.charAt(0).toUpperCase() || 'M' : 'M'}</AvatarFallback></Avatar></div>
        </header>

        <div className="p-4 md:p-6 overflow-y-auto flex-1">
          <h1 className="text-xl md:text-2xl font-bold">WhatsApp Automation</h1>
          <p className="text-muted-foreground mb-6 text-sm md:text-base">Manage client communications and automate messages</p>

          {loading ? <p>Loading data...</p> : error ? <p className="text-destructive">Error: {error}</p> : (
            <>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 mb-6"><div className="bg-card border-border border rounded-lg p-4 flex items-center gap-3"><MessageCircle className="w-6 h-6 text-primary" /><div><p className="text-muted-foreground text-sm">Messages Sent</p><h2 className="text-lg md:text-xl font-semibold">{stats.messagesSent}</h2></div></div><div className="bg-card border-border border rounded-lg p-4 flex items-center gap-3"><Users className="w-6 h-6 text-green-600" /><div><p className="text-muted-foreground text-sm">Active Contacts</p><h2 className="text-lg md:text-xl font-semibold">{stats.activeContacts}</h2></div></div><div className="bg-card border-border border rounded-lg p-4 flex items-center gap-3"><Clock className="w-6 h-6 text-purple-600" /><div><p className="text-muted-foreground text-sm">Scheduled</p><h2 className="text-lg md:text-xl font-semibold">{stats.scheduled}</h2></div></div></div>
              <div className="flex flex-col sm:flex-row gap-3 mb-6"><button className="bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded-lg text-sm font-medium flex items-center justify-center gap-2 transition-colors duration-300">Bulk Message</button><button onClick={() => setIsScheduling(true)} className="border-border border px-4 py-2 rounded-lg text-foreground hover:bg-muted text-sm font-medium">Schedule Message</button></div>
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 h-[65vh]">
                <div className="bg-card border-border border rounded-lg p-4 overflow-y-auto"><h2 className="text-foreground font-semibold mb-3">Contacts</h2><ul>{contacts.map((c) => (<li key={c.id} onClick={() => setSelectedContact(c)} className={`p-3 rounded-lg cursor-pointer mb-2 transition-colors ${selectedContact?.id === c.id ? "bg-primary/10 border-primary/20 border" : "hover:bg-muted"}`}><p className="font-medium text-foreground text-sm md:text-base">{c.name}</p><p className="text-xs md:text-sm text-muted-foreground">{c.phone}</p></li>))}</ul></div>
                <div className="lg:col-span-2 bg-card border-border border rounded-lg flex flex-col justify-center items-center text-muted-foreground text-sm">{selectedContact ? (<div className="flex flex-col w-full h-full justify-between"><div className="border-b border-border p-3 md:p-4 bg-muted flex justify-between items-center"><div><h2 className="font-medium text-foreground text-sm md:text-base">{selectedContact.name}</h2><p className="text-xs text-muted-foreground">{selectedContact.phone}</p></div><span className="text-xs text-muted-foreground hidden sm:block">Chat Window</span></div><div className="flex-1 flex items-center justify-center text-gray-400 text-xs md:text-sm px-2 text-center">Message history will appear here</div><div className="border-t border-border p-2 md:p-3 flex gap-2 md:gap-3">
                  <input 
                    type="text" 
                    placeholder="Type a message..." 
                    className="flex-1 border-border border rounded-lg px-3 py-2 text-sm bg-card" 
                    value={messageText} 
                    onChange={(e) => setMessageText(e.target.value)} 
                    onKeyDown={(e) => e.key === 'Enter' && !isSending && handleSendMessage()}
                  />
                  <button 
                    onClick={handleSendMessage} 
                    disabled={isSending} 
                    className="bg-primary hover:bg-primary/90 text-primary-foreground px-3 md:px-4 py-2 rounded-lg text-xs md:text-sm disabled:opacity-50"
                  >
                    {isSending ? 'Sending...' : 'Send'}
                  </button>
                </div></div>) : (<p className="text-xs md:text-sm text-center p-4">Select a contact to start messaging</p>)}</div>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}