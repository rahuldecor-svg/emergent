import { createContext, useContext, useEffect, useState } from "react";
import { http } from "@/lib/api";

const AuthCtx = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null); // null = checking, false = anon, obj = user
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        const { data } = await http.get("/auth/me");
        setUser(data);
      } catch {
        setUser(false);
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  const login = async (email, password) => {
    const { data } = await http.post("/auth/login", { email, password });
    setUser(data.user);
    return data.user;
  };

  const logout = async () => {
    try { await http.post("/auth/logout"); } catch { /* ignore */ }
    setUser(false);
  };

  return (
    <AuthCtx.Provider value={{ user, loading, login, logout, setUser }}>
      {children}
    </AuthCtx.Provider>
  );
}

export const useAuth = () => useContext(AuthCtx);
