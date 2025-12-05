"use client";

import { apiClient } from "@/lib/api-client";
import { useAuth } from "@/hooks/useAuth";
import { supabase } from "@/lib/supabaseClient";
import { Auth } from "@supabase/auth-ui-react";
import { ThemeSupa } from "@supabase/auth-ui-shared";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

export default function SignIn() {
  const router = useRouter();

  const [formData, setFormData] = useState({
    name: "",
    email: "",
    password: "",
    role: "",
    remember: false,
  });

  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    console.log("handleSubmit called");
    console.log("Email:", formData.email);
    console.log("Password:", formData.password);

    if (!formData.email || !formData.password) {
      toast({
        title: "Missing Fields",
        description: "Please enter email and password",
        variant: "destructive",
      });
      return;
    }

    const validEmail = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!validEmail.test(formData.email)) {
      toast({
        title: "Invalid Email",
        description: "Enter a valid email address",
        variant: "destructive",
      });
      return;
    }

    setLoading(true);

    const { data, error } = await supabase.auth.signInWithPassword({
      email: formData.email,
      password: formData.password,
    });

    console.log("Supabase auth data:", data);
    console.log("Supabase auth error:", error);

    if (error) {
      if (error.message.toLowerCase().includes("confirm")) {
        toast({
          title: "Email Not Verified",
          description: "Please confirm your email before logging in.",
          variant: "destructive",
        });

        await supabase.auth.resend({
          type: "signup",
          email: formData.email,
        });
        console.log("Resend request sent for:", formData.email);
      } else {
        toast({
          title: "Login Failed",
          description: error.message,
          variant: "destructive",
        });
      }
      setLoading(false);
      return;
    }

    // On success, store the user ID
    if (data.user) {
      localStorage.setItem("user_id", data.user.id);

              // Use the consistent apiClient to fetch user data
              const { data: user } = await apiClient.get('/api/users/me');
              if (user) {
                console.log("Redirecting to dashboard...");
                router.push("/dashboard");
              }    }
    setLoading(false);
  };

  return (
    <AuthCard
      title="BizzAuto"
      description="AI-Powered Business Automation Platform"
    >
      <form onSubmit={handleSubmit} className="space-y-5">
        {/* Email */}
        <div className="space-y-1">
          <Label>Email</Label>
          <Input
            type="email"
            placeholder="Enter Your Email"
            value={formData.email}
            onChange={(e) => setFormData({ ...formData, email: e.target.value })}
          />
        </div>

        <div className="relative">
          <Label>Password</Label>
          <input
            type={showPassword ? "text" : "password"}
            id="password"
            placeholder="Enter Your Password"
            value={formData.password}
            onChange={(e) =>
              setFormData({ ...formData, password: e.target.value })
            }
            className="w-full h-11 px-3 pr-10 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        {/* Remember Me */}
        <div className="flex items-center space-x-2">
          <Checkbox
            checked={formData.remember}
            onCheckedChange={(val) =>
              setFormData({ ...formData, remember: val as boolean })
            }
          />
          <Label className="cursor-pointer">Remember me</Label>
        </div>

        <Button
          type="submit"
          className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium"
          disabled={loading}
        >
          {loading ? "Signing in..." : "Sign In"}
        </Button>

        <div className="text-sm text-center text-gray-500">
          Don’t have an account?{" "}
          <button
            type="button"
            onClick={() => router.push("/signUp")}
            className="text-blue-600 font-semibold hover:underline"
          >
            Sign Up
          </button>
        </div>
      </form>
    </AuthCard>
  );
}
