import axios from "axios";

export const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

export const http = axios.create({
  baseURL: API,
  withCredentials: true,
});

export function formatApiError(detail) {
  if (detail == null) return "Something went wrong";
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail))
    return detail.map((e) => (e?.msg ? e.msg : JSON.stringify(e))).join(" ");
  if (detail?.msg) return detail.msg;
  return String(detail);
}
