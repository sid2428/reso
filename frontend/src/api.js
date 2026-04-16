import axios from "axios";

const BASE_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

const api = axios.create({ baseURL: BASE_URL });

export const analyzeImage = async (file, onUploadProgress) => {
  const form = new FormData();
  form.append("file", file);
  const { data } = await api.post("/analyze", form, {
    headers: { "Content-Type": "multipart/form-data" },
    onUploadProgress,
  });
  return data;
};

export const fetchHistory = async () => {
  const { data } = await api.get("/history");
  return data;
};

export default api;
