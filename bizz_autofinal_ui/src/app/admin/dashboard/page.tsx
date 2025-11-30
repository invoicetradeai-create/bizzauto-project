"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Users, Building2, DollarSign, Activity } from "lucide-react";

import { RevenueChart } from "@/components/admin/RevenueChart";
import { UserGrowthChart } from "@/components/admin/UserGrowthChart";
import { getAuthHeaders } from "@/lib/auth";

interface AnalyticsData {
    total_users: number;
    total_companies: number;
    total_revenue: number;
    active_users: number;
    revenue_trend: { name: string; value: number }[];
    user_growth: { name: string; value: number }[];
}

export default function AdminDashboard() {
    const [data, setData] = useState<AnalyticsData | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const headers = await getAuthHeaders();
                const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/admin/analytics`, {
                    headers
                });
                if (res.ok) {
                    const json = await res.json();
                    setData(json);
                }
            } catch (error) {
                console.error("Failed to fetch analytics:", error);
                console.error("Fetch URL:", `${process.env.NEXT_PUBLIC_API_URL}/api/admin/analytics`);
                setData(null);
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, []);

    if (loading) {
        return <div className="p-8 text-center">Loading dashboard...</div>;
    }

    if (!data) {
        return (
            <div className="p-8 text-center text-red-500">
                <p className="font-bold">Failed to load data</p>
                <p className="text-sm text-gray-500 mt-2">
                    Check console for details. Ensure backend is running at {process.env.NEXT_PUBLIC_API_URL || 'undefined'}
                </p>
            </div>
        );
    }

    return (
        <div className="space-y-6 text-gray-900 dark:text-gray-100">
            <h1 className="text-3xl font-bold text-gray-800 dark:text-white">Dashboard Overview</h1>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium text-gray-500 dark:text-gray-400">Total Users</CardTitle>
                        <Users className="h-4 w-4 text-blue-500" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold dark:text-white">{data.total_users}</div>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium text-gray-500 dark:text-gray-400">Total Companies</CardTitle>
                        <Building2 className="h-4 w-4 text-green-500" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold dark:text-white">{data.total_companies}</div>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium text-gray-500 dark:text-gray-400">Total Revenue</CardTitle>
                        <DollarSign className="h-4 w-4 text-yellow-500" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold dark:text-white">${data.total_revenue.toLocaleString()}</div>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium text-gray-500 dark:text-gray-400">Active Users</CardTitle>
                        <Activity className="h-4 w-4 text-purple-500" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold dark:text-white">{data.active_users}</div>
                    </CardContent>
                </Card>
            </div>

            {/* Charts */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
                <RevenueChart data={data.revenue_trend || []} />
                <UserGrowthChart data={data.user_growth || []} />
            </div>
        </div>
    );
}
