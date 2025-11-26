"use client";

import React, { useState, useEffect } from "react";
import { fetchUserById, User } from "@/lib/api"; // Adjust import path if necessary

const UserProfilePage = () => {
  // Example: Get userId from where you store it after login
  // This typically comes from your authentication context (e.g., Supabase session)
  const [userId, setUserId] = useState<string | null>(null);
  
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Effect to retrieve the userId (e.g., from local storage after login)
  useEffect(() => {
    // In a real app, this would come from your auth provider's session or context
    const loggedInUserId = localStorage.getItem("user_id"); 
    if (loggedInUserId) {
      setUserId(loggedInUserId);
    } else {
      setLoading(false);
      setError("User not logged in. Please sign in.");
    }
  }, []); // Run once on component mount

  // Effect to fetch user data when userId is available
  useEffect(() => {
    if (!userId) {
      // If userId is null (not logged in or not yet loaded), do nothing here
      return; 
    }

    const loadUserData = async () => {
      setLoading(true); // Start loading state
      setError(null);    // Clear previous errors
      try {
        const userData = await fetchUserById(userId);
        setUser(userData);
      } catch (err: any) {
        // Catch the error thrown by fetchUserById (e.g., "User not found", "Something went wrong")
        setError(err.message); 
      } finally {
        setLoading(false); // End loading state
      }
    };

    loadUserData(); // Call the async function
  }, [userId]); // Re-run this effect if userId changes

  if (loading) {
    return <div className="text-center p-8 text-blue-600">Loading user profile...</div>;
  }

  if (error) {
    return <div className="text-center p-8 text-red-500">Error: {error}</div>;
  }

  if (!user) {
    // This case should ideally be covered by the error state ("User not logged in")
    // or if a user with the ID was genuinely not found and fetchUserById threw.
    return <div className="text-center p-8 text-gray-700">No user data available.</div>;
  }

  // --- Render user data on success ---
  return (
    <div className="p-8 max-w-2xl mx-auto bg-white shadow-lg rounded-lg mt-10">
      <h1 className="text-3xl font-bold text-gray-800 mb-6 border-b pb-3">User Profile</h1>
      <div className="space-y-4 text-gray-700">
        <p><strong>ID:</strong> {user.id}</p>
        <p><strong>Full Name:</strong> {user.full_name}</p>
        <p><strong>Email:</strong> {user.email}</p>
        <p><strong>Role:</strong> {user.role}</p>
        <p><strong>Business Name:</strong> {user.business_name || "N/A"}</p>
        <p><strong>Location:</strong> {user.location || "N/A"}</p>
        <p><strong>Contact Number:</strong> {user.contact_number || "N/A"}</p>
      </div>
      <p className="mt-6 text-sm text-gray-500">
        To update these details, please contact support or use the settings page.
      </p>
    </div>
  );
};

export default UserProfilePage;
