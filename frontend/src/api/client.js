import axios from "axios";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "https://public-energy-api.onrender.com/api/v1";

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
});

export async function fetchEnergyData() {
  const { data } = await apiClient.get("/energy-data");
  return data;
}

export async function fetchHistoricalData() {
  const { data } = await apiClient.get("/historical-data");
  return Array.isArray(data) ? data : data?.value || [];
}

export async function fetchDailyTrends() {
  const { data } = await apiClient.get("/daily-trends");
  return data;
}

export default apiClient;
