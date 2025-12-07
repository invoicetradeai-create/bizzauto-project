"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { MessageCircle, AlertCircle, Clock } from "lucide-react";
import { apiClient } from "@/lib/api-client";

interface WhatsappStats {
    total_sent: number;
    total_failed: number;
    scheduled_pending: number;
}

export default function WhatsappReports() {
    const [stats, setStats] = useState<WhatsappStats | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchStats = async () => {
            try {
                const res = await apiClient.get<WhatsappStats>('/api/admin/whatsapp-stats');
                setStats(res.data);
            } catch (error) {
                console.error("Failed to fetch stats", error);
            } finally {
                setLoading(false);
            }
        };

        fetchStats();
    }, []);

    if (loading) return <div className="p-8">Loading stats...</div>;
    if (!stats) return <div className="p-8 text-red-500">Failed to load stats</div>;

    return (
        <div className="space-y-6 text-gray-900 dark:text-gray-100">
            <h1 className="text-3xl font-bold text-gray-800 dark:text-white">WhatsApp Analytics</h1>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <Card className="border-l-4 border-l-green-500">
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium text-gray-500 dark:text-gray-400">Messages Sent</CardTitle>
                        <MessageCircle className="h-4 w-4 text-green-500" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold dark:text-white">{stats.total_sent}</div>
                    </CardContent>
                </Card>

                <Card className="border-l-4 border-l-red-500">
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium text-gray-500 dark:text-gray-400">Failed Messages</CardTitle>
                        <AlertCircle className="h-4 w-4 text-red-500" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold dark:text-white">{stats.total_failed}</div>
                    </CardContent>
                </Card>

                <Card className="border-l-4 border-l-yellow-500">
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium text-gray-500 dark:text-gray-400">Scheduled (Pending)</CardTitle>
                        <Clock className="h-4 w-4 text-yellow-500" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold dark:text-white">{stats.scheduled_pending}</div>
                    </CardContent>
                </Card>
            </div>

            {/* Placeholder for detailed logs or charts */}
            <Card className="mt-6 h-[400px] flex items-center justify-center bg-slate-50 dark:bg-slate-900 border-dashed dark:border-slate-700">
                <span className="text-gray-400 dark:text-gray-500">Message Traffic Chart Placeholder</span>
            </Card>
        </div>
    );
}
