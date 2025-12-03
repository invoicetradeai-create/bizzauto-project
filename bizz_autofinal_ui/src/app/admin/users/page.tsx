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
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { toast } from "@/hooks/use-toast";
import { apiClient } from "@/lib/api-client";

interface User {
    id: string;
    full_name: string;
    email: string;
    role: string;
    status: string;
    company_id: string;
}

export default function UserManagement() {
    const [users, setUsers] = useState<User[]>([]);
    const [loading, setLoading] = useState(true);

    const fetchUsers = async () => {
        try {
            const res = await apiClient.get<User[]>('/api/admin/users');
            setUsers(res.data);
        } catch (error) {
            console.error("Failed to fetch users", error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchUsers();
    }, []);

    const handleStatusChange = async (userId: string, action: 'suspend' | 'activate') => {
        try {
            const res = await apiClient.post(`/api/admin/users/${userId}/${action}`);

            if (res.status === 200) {
                toast({
                    title: "Success",
                    description: `User ${action}ed successfully`,
                });
                fetchUsers(); // Refresh list
            } else {
                toast({
                    title: "Error",
                    description: "Failed to update user status",
                    variant: "destructive"
                });
            }
        } catch (error) {
            console.error("Error updating status", error);
        }
    };

    if (loading) return <div className="p-8">Loading users...</div>;

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-center">
                <h1 className="text-3xl font-bold text-gray-800 dark:text-white">User Management</h1>
                <Button onClick={fetchUsers}>Refresh List</Button>
            </div>

            <div className="bg-white dark:bg-slate-900 rounded-lg shadow border dark:border-slate-800 text-gray-900 dark:text-gray-100">
                <Table>
                    <TableHeader>
                        <TableRow>
                            <TableHead>Name</TableHead>
                            <TableHead>Email</TableHead>
                            <TableHead>Role</TableHead>
                            <TableHead>Status</TableHead>
                            <TableHead>Actions</TableHead>
                        </TableRow>
                    </TableHeader>
                    <TableBody>
                        {users.map((user) => (
                            <TableRow key={user.id}>
                                <TableCell className="font-medium">{user.full_name}</TableCell>
                                <TableCell>{user.email}</TableCell>
                                <TableCell>
                                    <Badge variant={user.role === 'admin' ? 'default' : 'secondary'}>
                                        {user.role}
                                    </Badge>
                                </TableCell>
                                <TableCell>
                                    <Badge variant={user.status === 'active' ? 'outline' : 'destructive'}>
                                        {user.status}
                                    </Badge>
                                </TableCell>
                                <TableCell>
                                    {user.role !== 'admin' && (
                                        <div className="flex space-x-2">
                                            {user.status === 'active' ? (
                                                <Button
                                                    variant="destructive"
                                                    size="sm"
                                                    onClick={() => handleStatusChange(user.id, 'suspend')}
                                                >
                                                    Suspend
                                                </Button>
                                            ) : (
                                                <Button
                                                    variant="outline"
                                                    size="sm"
                                                    className="text-green-600 border-green-600 hover:bg-green-50"
                                                    onClick={() => handleStatusChange(user.id, 'activate')}
                                                >
                                                    Activate
                                                </Button>
                                            )}
                                        </div>
                                    )}
                                </TableCell>
                            </TableRow>
                        ))}
                    </TableBody>
                </Table>
            </div>
        </div>
    );
}
