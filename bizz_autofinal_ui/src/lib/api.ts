import { apiClient } from "./api-client"; // Your configured axios instance

// Define a User interface for type safety
export interface User {
  id: string; // UUID from Supabase
  full_name: string;
  email: string;
  role: string;
  business_name?: string;
  location?: string;
  contact_number?: string;
}

/**
 * Fetches a single user by their ID from the backend API.
 * Handles errors and validation as requested.
 *
 * @param userId The UUID of the user to fetch.
 * @returns A Promise that resolves to the user data.
 * @throws An error with a user-friendly message if the fetch fails.
 */
export const fetchUserById = async (userId: string): Promise<User> => {
  // Basic validation
  if (!userId) {
    throw new Error("A user ID must be provided to fetch user data.");
  }

  try {
    const response = await apiClient.get<User>(`/api/users/${userId}`);
    return response.data;

  } catch (error: any) {
    if (error.response) {
      if (error.response.status === 404) {
        // This handles both a non-existent user and a non-existent API route.
        throw new Error("User not found");
      }
    } else if (error.request) {
      console.error("Network error:", error.request);
    } else {
      console.error("Error setting up request:", error.message);
    }
    
    // Generic fallback error message for any other issues
    throw new Error("Something went wrong while fetching user data.");
  }
};
