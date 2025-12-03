"use client";

import { useEffect, useState } from "react";
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { apiClient } from "@/lib/api-client";
import { API_ENDPOINTS } from "@/lib/api-config";

interface Invoice {
    id: string;
    invoice_date: string;
    total_amount: number;
    payment_status: string;
    notes: string;
}

export default function BillingPortal() {
    const [invoices, setInvoices] = useState<Invoice[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchBilling = async () => {
            try {
                const response = await apiClient.get<Invoice[]>(API_ENDPOINTS.adminBilling);
                setInvoices(response.data);
            } catch (error) {
                console.error("Failed to fetch billing", error);
            } finally {
                setLoading(false);
            }
        };

        fetchBilling();
    }, []);

    if (loading) return <div className="p-8">Loading billing data...</div>;

    return (
        <div className="space-y-6">
            <h1 className="text-3xl font-bold text-gray-800 dark:text-white">Billing Portal</h1>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <Card>
                    <CardHeader>
                        <CardTitle className="text-sm font-medium text-gray-500 dark:text-gray-400">Total Transactions</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold dark:text-white">{invoices.length}</div>
                    </CardContent>
                </Card>
                {/* Add more summary cards if needed */}
            </div>

            <div className="bg-white dark:bg-slate-900 rounded-lg shadow border dark:border-slate-800 text-gray-900 dark:text-gray-100">
                <Table>
                    <TableHeader>
                        <TableRow>
                            <TableHead>Date</TableHead>
                            <TableHead>Amount</TableHead>
                            <TableHead>Status</TableHead>
                            <TableHead>Notes</TableHead>
                        </TableRow>
                    </TableHeader>
                    <TableBody>
                        {invoices.map((inv) => (
                            <TableRow key={inv.id}>
                                <TableCell className="dark:text-gray-200">{new Date(inv.invoice_date).toLocaleDateString()}</TableCell>
                                <TableCell className="dark:text-gray-200">${inv.total_amount.toFixed(2)}</TableCell>
                                <TableCell>
                                    <Badge variant={inv.payment_status === 'paid' ? 'default' : 'secondary'}>
                                        {inv.payment_status}
                                    </Badge>
                                </TableCell>
                                <TableCell className="text-gray-500 dark:text-gray-400 text-sm">{inv.notes || "-"}</TableCell>
                            </TableRow>
                        ))}
                    </TableBody>
                </Table>
            </div>
        </div>
    );
}
