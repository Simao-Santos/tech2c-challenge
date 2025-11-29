const APIPort: string = import.meta.env.VITE_API_PORT ?? '7001';
const APIHost: string = import.meta.env.VITE_API_HOST ?? 'localhost';

const API_BASE_URL = `http://${APIHost}:${APIPort}/api`;

export interface EmissionRecord {
  id: number;
  company: string;
  year: number;
  sector: string;
  energy_consumption_mwh: string;
  co2_emissions_tons: string;
}

export interface ImportCSVResponse {
  message: string;
  created: number;
  updated: number;
  errors: string[];
  total_processed: number;
}

class ApiService {
  private getHeaders(includeContentType = true): HeadersInit {
    const headers: HeadersInit = {};
    
    if (includeContentType) {
      headers['Content-Type'] = 'application/json';
    }
    
    return headers;
  }

  async getAllEmissions(): Promise<EmissionRecord[]> {
    const response = await fetch(`${API_BASE_URL}/emissions/`, {
      headers: this.getHeaders(),
    });
    
    if (!response.ok) {
      throw new Error('Failed to fetch emissions data');
    }
    
    return response.json();
  }

  async importCSV(file: File): Promise<ImportCSVResponse> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_BASE_URL}/emissions/import_csv/`, {
      method: 'POST',
      headers: this.getHeaders(false), // Don't set Content-Type for FormData
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Failed to import CSV');
    }

    return response.json();
  }

}

export const api = new ApiService();