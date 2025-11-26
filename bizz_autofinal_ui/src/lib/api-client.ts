import axios from "axios";

const baseURL = process.env.NEXT_PUBLIC_API_URL || "https://bizzauto-project.onrender.com";
console.log("🚀 API Client Base URL:", baseURL);

const apiClient = axios.create({
  baseURL: baseURL,
  headers: {
    "Content-Type": "application/json",
  },
});

apiClient.interceptors.request.use((config) => {
  if (typeof window !== "undefined") {
    const userId = localStorage.getItem("user_id");
    if (userId) {
      config.headers["X-User-Id"] = userId;
    }
  }
  return config;
});

export { apiClient };
