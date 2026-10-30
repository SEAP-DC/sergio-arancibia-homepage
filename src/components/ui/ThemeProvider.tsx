import { useCallback, useEffect, useState, type ReactNode } from "react";
import { ThemeContext, type Theme } from "../../hooks/use-theme";

const STORAGE_KEY = "sa-theme";

/** localStorage puede estar bloqueado (file://, modo privado): no debe romper la app. */
function readStoredTheme(): string | null {
  try {
    return localStorage.getItem(STORAGE_KEY);
  } catch {
    return null;
  }
}

function writeStoredTheme(value: Theme): void {
  try {
    localStorage.setItem(STORAGE_KEY, value);
  } catch {
    /* sin persistencia: el tema igual aplica en la sesión */
  }
}

function getInitialTheme(): Theme {
  if (typeof window === "undefined") return "dark";
  const stored = readStoredTheme();
  if (stored === "light" || stored === "dark") return stored;
  // Diseño oscuro-first (paleta AI Data Lab): claro solo si el sistema lo pide.
  return window.matchMedia("(prefers-color-scheme: light)").matches
    ? "light"
    : "dark";
}

export function ThemeProvider({ children }: { children: ReactNode }) {
  const [theme, setTheme] = useState<Theme>(getInitialTheme);

  useEffect(() => {
    // "dark" alimenta la variante Tailwind dark:; "light" activa los tokens claros.
    document.documentElement.classList.toggle("dark", theme === "dark");
    document.documentElement.classList.toggle("light", theme === "light");
    writeStoredTheme(theme);
  }, [theme]);

  // Sigue el sistema si el usuario nunca eligió explícitamente.
  useEffect(() => {
    const media = window.matchMedia("(prefers-color-scheme: light)");
    const onChange = (e: MediaQueryListEvent) => {
      if (!readStoredTheme()) {
        setTheme(e.matches ? "light" : "dark");
      }
    };
    media.addEventListener("change", onChange);
    return () => media.removeEventListener("change", onChange);
  }, []);

  const toggleTheme = useCallback(() => {
    setTheme((t) => (t === "dark" ? "light" : "dark"));
  }, []);

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
}
