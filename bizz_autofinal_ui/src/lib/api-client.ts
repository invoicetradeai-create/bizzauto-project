import { API_CONFIG } from './api-config';

export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = 'ApiError';
  }
}

export interface ApiResponse<T> {
  data?: T;
  error?: string;
  status: number;
}

class ApiClient {
  private baseUrl: string;

  constructor() {
    this.baseUrl = API_CONFIG.BASE_URL.replace(/\/+$/, '');
    console.log("BASE_URL =", this.baseUrl);
  }

  private buildUrl(endpoint: string): string {
    const cleanEndpoint = endpoint.replace(/^\/+/, '');
    return `${this.baseUrl}/${cleanEndpoint}`;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {

    const url = this.buildUrl(endpoint);
    console.log(`🔵 API Request: ${options.method || 'GET'} ${url}`);

    const config: RequestInit = {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    };

    try {
      const response = await fetch(url, config);

      let data;
      const contentType = response.headers.get('content-type');

      if (contentType && contentType.includes('application/json')) {
        data = await response.json();
      } else {
        data = await response.text();
      }

      console.log(`✅ API Response: ${response.status}`, data);

      if (!response.ok) {
        throw new ApiError(
          response.status,
          data?.detail || data?.message || 'An error occurred'
        );
      }

      return { data, status: response.status };
    } catch (error) {
      console.error('❌ API Error:', error);

      if (error instanceof ApiError) {
        return { error: error.message, status: error.status };
      }

      return {
        error: error instanceof Error ? error.message : 'Network error',
        status: 0,
      };
    }
  }

  async get<T>(endpoint: string): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, { method: 'GET' });
  }

  async post<T>(endpoint: string, data: any): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async put<T>(endpoint: string, data: any): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async delete<T>(endpoint: string): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, { method: 'DELETE' });
  }
}

export const apiClient = new ApiClient();
