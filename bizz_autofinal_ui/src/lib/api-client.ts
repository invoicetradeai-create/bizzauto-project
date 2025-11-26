import axios from "axios";

const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || "https://bizzauto-project.onrender.com",
  headers: {
    "Content-Type": "application/json",
  },
});

<<<<<<< HEAD
export { apiClient };
=======
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
>>>>>>> 15e70f7dfee8b8712abec96744c07aa12709460f
