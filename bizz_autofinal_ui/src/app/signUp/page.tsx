"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import AuthCard from "@/components/AuthCard";

import { supabase } from "@/lib/supabaseClient";
import { apiClient } from "@/lib/api-client";

export default function SignUpPage() {
  const router = useRouter();
  const [formData, setFormData] = useState({
    fullName: "",
    email: "",
    password: "",
    role: "",
  });

  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!formData.fullName || !formData.email || !formData.password || !formData.role) {
      toast.error("Please fill in all fields");
      return;
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(formData.email)) {
      toast.error("Please enter a valid email address");
      return;
    }

    if (formData.password.length < 6) {
      toast.error("Password must be at least 6 characters");
      return;
    }

    setLoading(true);

    try {
      // First, get the company ID
      let companyId;
      try {
        const companiesResponse = await apiClient.get("/api/companies");
        if (!companiesResponse.data || companiesResponse.data.length === 0) {
          throw new Error("No company configured. Please contact support.");
        }
        companyId = companiesResponse.data[0].id;
      } catch (companyErr: any) {
        toast.error(companyErr.message || "Failed to fetch company information.");
        setLoading(false);
        return;
      }


      const { data, error: supabaseError } = await supabase.auth.signUp({
        email: formData.email,
        password: formData.password,
        options: {
          data: {
            full_name: formData.fullName,
            role: formData.role,
          },
                 },
      });

      if (supabaseError) {
        toast.error(supabaseError.message);
        setLoading(false);
        return;
      }

      // After successful Supabase signup, create the user in the public.users table
      if (data.user) {
        const newUser = {
          id: data.user.id,
          company_id: companyId, // Add the company ID
          full_name: formData.fullName,
          email: formData.email,
          role: formData.role,
        };

        try {
          await apiClient.post("/api/users", newUser);
        } catch (apiErr: any) {
          console.error("API Exception creating user:", apiErr);
          toast.error(apiErr.response?.data?.detail || apiErr.message || "User profile creation failed");
          await supabase.auth.signOut(); // Rollback Supabase signup if API user creation fails
          setLoading(false);
          return;
        }
      }

      toast.success("Signup successful! You can now sign in.");
      setLoading(false);
      router.push("/signin");
    } catch (err: any) { // This catch block handles errors from Supabase signup or unexpected errors
      // Already handled supabaseError, this is for any unhandled exceptions
      if (!err.message.includes("Failed to fetch company information") && !err.message.includes("User profile creation failed")) {
        toast.error(err?.message || "Signup failed");
      }
      setLoading(false);
    }
  };

  return (
    <AuthCard title="BizzAuto" description="Create your business account">
      <form onSubmit={handleSubmit} className="space-y-5 mt-2">

        {/* FULL NAME */}
        <div className="space-y-1">
          <Label htmlFor="fullName" className="text-sm font-medium">
            Full Name
          </Label>
          <Input
            id="fullName"
            placeholder="Ahmed Khan"
            value={formData.fullName}
            onChange={(e) =>
              setFormData({ ...formData, fullName: e.target.value })
            }
            className="h-11 bg-gray-100 border border-gray-200 focus:bg-white"
          />
        </div>

        {/* EMAIL */}
        <div className="space-y-1">
          <Label htmlFor="email" className="text-sm font-medium">
            Email
          </Label>
          <Input
            id="email"
            type="email"
            placeholder="ahmed@company.com"
            value={formData.email}
            onChange={(e) =>
              setFormData({ ...formData, email: e.target.value })
            }
            className="h-11 bg-gray-100 border border-gray-200 focus:bg-white"
          />
        </div>

        {/* PASSWORD */}
        <div className="space-y-1">
          <Label htmlFor="password" className="text-sm font-medium">
            Password
          </Label>
          <div className="relative">
            <Input
              id="password"
              type={showPassword ? "text" : "password"}
              placeholder="••••••••"
              value={formData.password}
              onChange={(e) =>
                setFormData({ ...formData, password: e.target.value })
              }
              className="h-11 bg-gray-100 border border-gray-200 focus:bg-white pr-12"
            />
          </div>
        </div>

        {/* ROLE */}
        <div className="space-y-1">
          <Label htmlFor="role" className="text-sm font-medium">
            Role
          </Label>
          <Select
            value={formData.role}
            onValueChange={(value) =>
              setFormData({ ...formData, role: value })
            }
          >
            <SelectTrigger
              id="role"
              className="h-11 bg-gray-100 border border-gray-200 focus:bg-white"
            >
              <SelectValue placeholder="Select your role" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="user">User</SelectItem>
              <SelectItem value="trader">Trader</SelectItem>
            </SelectContent>
          </Select>
        </div>

        {/* SUBMIT BUTTON */}
        <Button
          type="submit"
          className="w-full h-11 text-white bg-blue-600 hover:bg-blue-700 font-medium rounded-md"
          disabled={loading}
        >
          {loading ? "Creating..." : "Create Account"}
        </Button>

        {/* FOOTER */}
        <div className="text-center text-sm text-gray-500 mt-3">
          Already have an account?{" "}
          <button
            type="button"
            onClick={() => router.push("/signin")}
            className="text-blue-600 font-medium hover:underline"
          >
            Sign In
          </button>
        </div>
      </form>
    </AuthCard>
  );
}
