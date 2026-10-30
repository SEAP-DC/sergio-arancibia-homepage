import { useEffect, useRef, useState } from "react";
import { Menu, Moon, Sun, X } from "lucide-react";
import { navItems, hero, site } from "../../data/content";
import { useTheme } from "../../hooks/use-theme";
import { cn } from "../../utils/cn";
import { Button } from "../ui/Button";
import { Logo } from "../ui/Logo";

function ThemeToggle() {
  const { theme, toggleTheme } = useTheme();
  return (
    <button
      type="button"
      onClick={toggleTheme}
      aria-label={
        theme === "dark" ? "Cambiar a modo claro" : "Cambiar a modo oscuro"
      }
      className="inline-flex h-9 w-9 items-center justify-center rounded-full text-muted transition-colors hover:bg-card-2 hover:text-ink focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent"
    >
      {theme === "dark" ? (
        <Sun size={17} aria-hidden="true" />
      ) : (
        <Moon size={16} aria-hidden="true" />
      )}
    </button>
  );
}

/** Marca en la navegación qué sección se está leyendo (aria-current). */
function useActiveSection(): string | null {
  const [active, setActive] = useState<string | null>(null);

  useEffect(() => {
    const sections = navItems
      .map((item) => document.getElementById(item.href.slice(1)))
      .filter((el): el is HTMLElement => el !== null);
    if (!sections.length) return;

    // Sección activa = la que ocupa la franja central de la ventana.
    const observer = new IntersectionObserver(
      (entries) => {
        const visible = entries
          .filter((e) => e.isIntersecting)
          .sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];
        if (visible) setActive(visible.target.id);
      },
      { rootMargin: "-25% 0px -55% 0px", threshold: [0, 0.25, 0.5, 1] },
    );

    for (const section of sections) observer.observe(section);
    return () => observer.disconnect();
  }, []);

  return active;
}

export function Header() {
  const [menuOpen, setMenuOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  const activeSection = useActiveSection();
  const menuButtonRef = useRef<HTMLButtonElement>(null);

  // Apenas se despega del inicio: sombra sutil, el header fijo se lee como capa.
  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 8);
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  // Cierra el menú móvil con Escape y al redimensionar a desktop.
  useEffect(() => {
    if (!menuOpen) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        setMenuOpen(false);
        // Devuelve el foco al botón: si no, el teclado queda "a la deriva".
        menuButtonRef.current?.focus();
      }
    };
    const onResize = () => {
      if (window.innerWidth >= 768) setMenuOpen(false);
    };
    window.addEventListener("keydown", onKey);
    window.addEventListener("resize", onResize);
    return () => {
      window.removeEventListener("keydown", onKey);
      window.removeEventListener("resize", onResize);
    };
  }, [menuOpen]);

  const nav = (mobile: boolean) =>
    navItems.map((item) => {
      const isActive = activeSection === item.href.slice(1);
      return (
        <a
          key={item.href}
          href={item.href}
          onClick={() => setMenuOpen(false)}
          aria-current={isActive ? "true" : undefined}
          className={cn(
            "rounded-lg transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent",
            mobile
              ? cn(
                  "block px-3 py-3 text-base font-medium hover:bg-card-2",
                  isActive ? "bg-card-2 text-accent-text" : "text-ink",
                )
              : cn(
                  "px-3 py-2 text-sm font-medium hover:text-ink",
                  isActive ? "text-accent-text" : "text-muted",
                ),
          )}
        >
          {item.label}
        </a>
      );
    });

  return (
    <header
      className={cn(
        "sticky top-0 z-50 border-b border-line bg-bg/80 backdrop-blur-md transition-shadow duration-200",
        scrolled && "shadow-lg shadow-black/5 dark:shadow-black/30",
      )}
    >
      <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-4 sm:px-6">
        <Logo />

        {/* Navegación desktop */}
        <nav aria-label="Principal" className="hidden md:block">
          <ul className="flex items-center gap-1">{nav(false)}</ul>
        </nav>

        <div className="flex items-center gap-2">
          <ThemeToggle />
          <Button href={hero.ctaPrimary.href} variant="primary" className="hidden sm:inline-flex">
            Ver proyectos
          </Button>
          {/* Menú móvil */}
          <button
            ref={menuButtonRef}
            type="button"
            onClick={() => setMenuOpen((o) => !o)}
            aria-expanded={menuOpen}
            aria-controls="mobile-menu"
            aria-label={menuOpen ? "Cerrar menú" : "Abrir menú"}
            className="inline-flex h-9 w-9 items-center justify-center rounded-full text-muted transition-colors hover:bg-card-2 hover:text-ink focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent md:hidden"
          >
            {menuOpen ? (
              <X size={18} aria-hidden="true" />
            ) : (
              <Menu size={18} aria-hidden="true" />
            )}
          </button>
        </div>
      </div>

      {/* Panel móvil: siempre en el DOM, para que aria-controls apunte a un elemento real.
          El key fuerza la animación de entrada en cada apertura. */}
      <nav
        key={menuOpen ? "abierto" : "cerrado"}
        id="mobile-menu"
        aria-label="Principal (móvil)"
        hidden={!menuOpen}
        className="animate-menu-in border-t border-line bg-bg px-4 pb-5 pt-2 md:hidden"
      >
        <ul>{nav(true)}</ul>
        <div className="mt-3 flex items-center gap-3 border-t border-line px-3 pt-4">
          <Button href={hero.ctaPrimary.href} className="flex-1">
            Ver proyectos
          </Button>
          <span className="text-sm text-faint">{site.role}</span>
        </div>
      </nav>
    </header>
  );
}
