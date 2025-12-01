"use client";

import { useState, useEffect, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useTheme } from "@/hooks/use-theme";
import { Button } from "@/components/ui/button";
import { Moon, Sun, Bell, Menu, Search, User, Mail, Phone, Building, Lock, Key } from "lucide-react";
import Sidebar, { NavigationContent } from "@/components/Sidebar";
import { Input } from "@/components/ui/input";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Sheet, SheetContent, SheetTrigger, SheetHeader, SheetTitle } from "@/components/ui/sheet";
import { apiClient } from "@/lib/api-client";

type UUID = string;

// Define types for the settings values
type ProfileSettings = {
  fullName: string;
  phone: string;
  email: string;
  company: string;
};

type NotificationSettings = {
  push: boolean;
  email: boolean;
  clientRegistration: boolean;
  paymentReceived: boolean;
  lowStock: boolean;
  overdueInvoices: boolean;
  whatsappMessage: boolean;
};

type IntegrationSettings = {
  whatsappApi: string;
  gmailApi: string;
};

// Main setting object from backend
type Setting = {
  id: UUID;
  user_id: UUID;
  key: string;
  value: ProfileSettings | NotificationSettings | IntegrationSettings | any;
};

type UserType = {
  id: UUID;
  full_name: string;
  email: string;
};

function SettingsContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { theme, toggleTheme, mounted } = useTheme();

  const initialTab = searchParams.get("tab");
  // Capitalize the first letter if it exists, otherwise default to "Profile"
  const defaultTab = initialTab
    ? initialTab.charAt(0).toUpperCase() + initialTab.slice(1)
    : "Profile";

  const [activeTab, setActiveTab] = useState(defaultTab);
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [userId, setUserId] = useState<UUID | null>(null);

  // State to hold all settings fetched from backend
  const [settings, setSettings] = useState<Record<string, any>>({
    profile: { fullName: "", phone: "", email: "", company: "" },
    notifications: { push: true, email: true, clientRegistration: true, paymentReceived: true, lowStock: true, overdueInvoices: true, whatsappMessage: false },
    integrations: { whatsappApi: "", gmailApi: "" },
    alerts: { phone: "" },
  });

  // State to map setting keys to their database IDs
  const [settingsMap, setSettingsMap] = useState<Record<string, UUID>>({});

  useEffect(() => {
    // Sync active tab with URL
    const tab = searchParams.get("tab");
    if (tab) {
      setActiveTab(tab.charAt(0).toUpperCase() + tab.slice(1));
    }
  }, [searchParams]);

  const handleTabClick = (tab: string) => {
    setActiveTab(tab);
    router.push(`/settings?tab=${tab.toLowerCase()}`);
  };

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setError(null);
      try {
        // 1. Fetch users to get a valid user ID
        const usersRes = await apiClient.get<UserType[]>('/api/users');
        const users = usersRes.data;

        if (!users || users.length === 0) {
          throw new Error("No users found. Cannot manage settings.");
        }
        const currentUserId = users[0].id;
        setUserId(currentUserId);

        // 2. Fetch all settings
        const settingsRes = await apiClient.get<Setting[]>('/tables/settings/');
        if (settingsRes.data) {
          const newSettings: Record<string, any> = {};
          const newSettingsMap: Record<string, UUID> = {};

          // 3. Filter settings for the current user and parse the value
          const userSettings = settingsRes.data.filter(s => s.user_id === currentUserId);
          userSettings.forEach(setting => {
            try {
              // The 'value' from the DB might be a stringified JSON, so we parse it.
              newSettings[setting.key] = typeof setting.value === 'string'
                ? JSON.parse(setting.value)
                : setting.value;
            } catch (e) {
              console.error(`Failed to parse setting value for key: ${setting.key}`, e);
              newSettings[setting.key] = {}; // Default to empty object on parse error
            }
            newSettingsMap[setting.key] = setting.id;
          });

          setSettings(prev => ({ ...prev, ...newSettings }));
          setSettingsMap(newSettingsMap);
        } else {
          // If no data, but no error thrown by Axios, it's an empty response
          // This case should ideally not throw an error, but just initialize with defaults
        }
      } catch (err: any) { // Catch block already exists
        setError(err.response?.data?.detail || err.message || "An unknown error occurred");
        console.error("Error fetching settings:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const handleSettingChange = (key: string, field: string, value: any) => {
    setSettings(prev => ({
      ...prev,
      [key]: {
        ...prev[key],
        [field]: value,
      },
    }));
  };

  const handleSave = async (key: string) => {
    if (!userId) {
      alert("User ID not found. Cannot save settings.");
      return;
    }
    const settingId = settingsMap[key];
    const data = {
      user_id: userId,
      key: key,
      value: settings[key],
    };

    try {
      if (settingId) {
        // Update existing setting
        await apiClient.put(`/tables/settings/${settingId}`, data);
      } else {
        // Create new setting
        await apiClient.post('/tables/settings/', data);
      }
      alert(`${key.charAt(0).toUpperCase() + key.slice(1)} settings saved!`);
    } catch (err: any) {
      alert(`Error saving ${key} settings: ${err.response?.data?.detail || err.message}`);
      console.error("Error saving settings:", err);
    }
  };

  return (
    <div className="flex min-h-screen bg-background overflow-hidden">
      <Sidebar />
      <div className="flex-1 flex flex-col transition-all duration-300 lg:ml-64">
        <header className="border-b bg-card px-4 py-3 flex items-center justify-between sticky top-0 z-40">
          <div className="flex items-center gap-3 flex-1">
            <Sheet open={open} onOpenChange={setOpen}><SheetTrigger asChild className="lg:hidden"><Button variant="outline" size="icon"><Menu className="h-5 w-5" /></Button></SheetTrigger><SheetContent side="left" className="p-0 w-64"><SheetHeader className="px-4 py-2 border-b"><SheetTitle>Dashboard Navigation</SheetTitle></SheetHeader><NavigationContent setOpen={setOpen} /></SheetContent></Sheet>
            <div className="relative flex-1 max-w-full"><Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" /><Input placeholder="Search anything..." className="pl-10 w-full" /></div>
          </div>
          <div className="flex items-center gap-1">
            <Button variant="ghost" size="icon" className="relative"><Bell className="h-4 w-4" /><span className="absolute -top-1 -right-1 h-3.5 w-3.5 bg-destructive rounded-full text-xs flex items-center justify-center">3</span></Button>
            <Button variant="ghost" size="icon" onClick={toggleTheme}>{mounted && theme === "dark" ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}</Button>
            <div onClick={() => router.push('/settings')} className="cursor-pointer hover:scale-105 transition-transform duration-200">
              <Avatar>
                <AvatarFallback className="bg-primary text-primary-foreground">{mounted ? localStorage.getItem("user_avatar")?.charAt(0).toUpperCase() || 'M' : 'M'}</AvatarFallback>
              </Avatar>
            </div>
          </div>
        </header>

        <div className="flex-1 overflow-y-auto p-6">
          <h1 className="text-2xl font-bold">Settings</h1>
          <p className="text-muted-foreground mb-6">Manage your account settings and preferences</p>

          <div className="flex flex-wrap gap-3 mb-6">
            {["Profile", "Notifications", "Integrations", "Alerts"].map((tab) => (
              <button key={tab} onClick={() => handleTabClick(tab)} className={`px-4 py-2 rounded-full text-sm font-medium shadow transition-colors ${activeTab === tab ? "bg-blue-600 text-white" : "bg-card hover:bg-muted"}`}>
                {tab}
              </button>
            ))}
          </div>

          {loading ? <p>Loading settings...</p> : error ? <p className="text-destructive">{error}</p> : (
            <>
              {activeTab === "Profile" && (
                <div className="bg-card border rounded-lg p-6">
                  <h2 className="text-lg font-semibold mb-4">Profile</h2>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {(Object.keys(settings.profile) as Array<keyof ProfileSettings>).map((key) => (
                      <div key={key}>
                        <label className="text-sm mb-1 block capitalize">{key.replace(/([A-Z])/g, ' ')}</label>
                        <div className="relative">
                          <User className="absolute left-3 top-2.5 w-4 h-4 text-gray-400" />
                          <input value={settings.profile[key]} onChange={(e) => handleSettingChange('profile', key, e.target.value)} className="w-full border rounded-lg pl-9 pr-3 py-2 text-sm bg-card" />
                        </div>
                      </div>
                    ))}
                  </div>
                  <div className="mt-8 flex justify-end">
                    <Button onClick={() => handleSave('profile')}>Save Changes</Button>
                  </div>
                </div>
              )}

              {activeTab === "Notifications" && (
                <div className="bg-card border rounded-lg p-6">
                  <h2 className="text-lg font-semibold mb-4">Notification Preferences</h2>
                  <div className="space-y-4">
                    {(Object.keys(settings.notifications) as Array<keyof NotificationSettings>).map((key) => (
                      <div key={key} className="flex items-center justify-between border-b py-2 text-sm">
                        <span className="capitalize">{key.replace(/([A-Z])/g, ' ')}</span>
                        <button onClick={() => handleSettingChange('notifications', key, !settings.notifications[key])} className={`relative w-12 h-6 rounded-full transition-colors ${settings.notifications[key] ? "bg-primary" : "bg-muted"}`}>
                          <span className={`absolute top-1 left-1 w-4 h-4 bg-white rounded-full transition-transform ${settings.notifications[key] ? "translate-x-6" : ""}`}></span>
                        </button>
                      </div>
                    ))}
                  </div>
                  <div className="mt-8 flex justify-end">
                    <Button onClick={() => handleSave('notifications')}>Save Preferences</Button>
                  </div>
                </div>
              )}

              {activeTab === "Integrations" && (
                <div className="bg-card border rounded-lg p-6">
                  <h2 className="text-lg font-semibold mb-4">API Integrations</h2>
                  <div className="space-y-6">
                    {(Object.keys(settings.integrations) as Array<keyof IntegrationSettings>).map((key) => (
                      <div key={key}>
                        <label className="text-sm font-medium capitalize">{key.replace(/([A-Z])/g, ' ')}</label>
                        <div className="relative mt-1">
                          <Key className="absolute left-3 top-2.5 w-4 h-4 text-muted-foreground" />
                          <input value={settings.integrations[key]} onChange={(e) => handleSettingChange('integrations', key, e.target.value)} className="w-full border rounded-lg pl-9 pr-3 py-2 bg-card" />
                        </div>
                      </div>
                    ))}
                  </div>
                  <div className="mt-8 flex justify-end">
                    <Button onClick={() => handleSave('integrations')}>Save API Keys</Button>
                  </div>
                </div>
              )}

              {activeTab === "Alerts" && (
                <div className="bg-card border rounded-lg p-6">
                  <h2 className="text-lg font-semibold mb-4">Alert Settings</h2>
                  <div className="space-y-6">
                    <div>
                      <label className="text-sm font-medium">Admin WhatsApp Number</label>
                      <div className="relative mt-1">
                        <Phone className="absolute left-3 top-2.5 w-4 h-4 text-muted-foreground" />
                        <input value={settings.alerts.phone} onChange={(e) => handleSettingChange('alerts', 'phone', e.target.value)} className="w-full border rounded-lg pl-9 pr-3 py-2 bg-card" />
                      </div>
                    </div>
                  </div>
                  <div className="mt-8 flex justify-end">
                    <Button onClick={() => handleSave('alerts')}>Save Alert Settings</Button>
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
}

export default function SettingsPage() {
  return (
    <Suspense fallback={<div>Loading settings...</div>}>
      <SettingsContent />
    </Suspense>
  );
}
