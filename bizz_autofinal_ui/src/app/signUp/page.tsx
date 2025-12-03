"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import AuthCard from "@/components/AuthCard";

import { supabase } from "@/lib/supabaseClient";
import { apiClient } from "@/lib/api-client";

export default function SignUpPage() {
  const router = useRouter();
  const [formData, setFormData] = useState({
    fullName: "",
    email: "",
    password: "",
    businessName: "",
    contactNumber: "",
    location: "",
  });

  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { id, value } = e.target;
    setFormData((prev) => ({ ...prev, [id]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (
      !formData.fullName ||
      !formData.email ||
      !formData.password ||
      !formData.businessName ||
      !formData.contactNumber ||
      !formData.location
    ) {
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
      let companyId;
      try {
        const companiesResponse = await apiClient.get("/api/companies");
        if (!companiesResponse.data || companiesResponse.data.length === 0) {
          throw new Error("No company configured. Please contact support.");
        }
        companyId = companiesResponse.data[0].id;
      } catch (companyErr: any) {
        toast.error(
          companyErr.message || "Failed to fetch company information."
        );
        setLoading(false);
        return;
      }

      const { data, error: supabaseError } = await supabase.auth.signUp({
        email: formData.email,
        password: formData.password,
        options: {
          data: {
            full_name: formData.fullName,
            business_name: formData.businessName,
            contact_number: formData.contactNumber,
            location: formData.location,
            role: "user", // Add default role
          },
          emailRedirectTo: `${window.location.origin}/verify-email`,
        },
      });

      if (supabaseError) {
        toast.error(supabaseError.message);
        setLoading(false);
        return;
      }

      if (data.user) {
        const newUser = {
          id: data.user.id,
          company_id: companyId,
          full_name: formData.fullName,
          email: formData.email,
          business_name: formData.businessName,
          contact_number: formData.contactNumber,
          location: formData.location,
          role: "user", // Add default role
        };

        try {
          await apiClient.post("/api/users", newUser);
        } catch (apiErr: any) {
          console.error("API Exception creating user:", apiErr);
          toast.error(
            apiErr.response?.data?.detail ||
              apiErr.message ||
              "User profile creation failed"
          );
          await supabase.auth.signOut();
          setLoading(false);
          return;
        }
      }

      toast.success("Signup successful! Please check your email to confirm.");
      router.push("/signin");
    } catch (err: any) {
      if (
        !err.message.includes("Failed to fetch company information") &&
        !err.message.includes("User profile creation failed")
      ) {
        toast.error(err?.message || "Signup failed");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthCard
      title="BizzAuto"
      description="Create your business account to get started"
    >
      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Full Name */}
        <div className="space-y-1">
          <Label htmlFor="fullName">Full Name</Label>
          <Input
            id="fullName"
            placeholder="Ahmed Khan"
            value={formData.fullName}
            onChange={handleInputChange}
          />
        </div>

        {/* Email */}
        <div className="space-y-1">
          <Label htmlFor="email">Email</Label>
          <Input
            id="email"
            type="email"
            placeholder="ahmed@company.com"
            value={formData.email}
            onChange={handleInputChange}
          />
        </div>

        {/* Password */}
        <div className="space-y-1">
          <Label htmlFor="password">Password</Label>
          <div className="relative">
            <Input
              id="password"
              type={showPassword ? "text" : "password"}
              placeholder="••••••••"
              value={formData.password}
              onChange={handleInputChange}
              className="pr-12"
            />
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className="absolute inset-y-0 right-0 px-3 flex items-center text-sm text-gray-600"
            >
              {showPassword ? "Hide" : "Show"}
            </button>
          </div>
        </div>

        {/* Business Name */}
        <div className="space-y-1">
          <Label htmlFor="businessName">Business Name</Label>
          <Input
            id="businessName"
            placeholder="e.g. Khan Autos"
            value={formData.businessName}
            onChange={handleInputChange}
          />
        </div>

        {/* Contact Number */}
        <div className="space-y-1">
          <Label htmlFor="contactNumber">Contact Number</Label>
          <Input
            id="contactNumber"
            placeholder="0300-1234567"
            value={formData.contactNumber}
            onChange={handleInputChange}
          />
        </div>

        {/* Location */}
        <div className="space-y-1">
          <Label htmlFor="location">Location</Label>
          <Input
            id="location"
            placeholder="e.g. Karachi, Pakistan"
            value={formData.location}
            onChange={handleInputChange}
          />
        </div>

        {/* SUBMIT BUTTON */}
        <Button
          type="submit"
          className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium"
          disabled={loading}
        >
          {loading ? "Creating Account..." : "Create Account"}
        </Button>

        {/* FOOTER */}
        <div className="text-center text-sm text-gray-500">
          Already have an account?{" "}
          <button
            type="button"
            onClick={() => router.push("/signin")}
            className="text-blue-600 font-semibold hover:underline"
          >
            Sign In
          </button>
        </div>
      </form>
    </AuthCard>
  );
}
