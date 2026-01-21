import axios from 'axios';
import { DashboardData } from './types';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const fetchMetrics = async (): Promise<DashboardData> => {
    const response = await axios.get(`${API_URL}/metrics`);
    return response.data;
};

export const seedData = async () => {
    await axios.post(`${API_URL}/seed`);
};
