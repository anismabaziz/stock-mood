import axios from "axios";

const axiosClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
  timeout: 60000,
  headers: {
    "Content-Type": "application/json",
  },
});

export default axiosClient;
