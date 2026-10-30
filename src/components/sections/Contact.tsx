import { ArrowUpRight, Mail } from "lucide-react";
import { contact, site } from "../../data/content";
import { Button } from "../ui/Button";
import { Reveal } from "../ui/Reveal";

/** Final CTA + contacto: el paso siguiente es claro y de un solo clic. */
export function Contact() {
  const mailto = `mailto:${site.email}?subject=${encodeURIComponent(
    "Hablemos de tus datos",
  )}`;

  return (
    <section id="contacto" aria-labelledby="contacto-title" className="scroll-mt-20 border-t border-line bg-card-2/40 py-16 sm:py-24">
      <div className="mx-auto max-w-3xl px-4 text-center sm:px-6">
        <Reveal>
          <span
            aria-hidden="true"
            className="inline-flex h-12 w-12 items-center justify-center rounded-2xl bg-accent-soft text-accent-text"
          >
            <Mail size={22} strokeWidth={2.1} />
          </span>
        </Reveal>

        <Reveal delay={80}>
          <h2
            id="contacto-title"
            className="mt-6 font-display text-3xl font-semibold tracking-tight sm:text-4xl"
          >
            {contact.heading}
          </h2>
        </Reveal>

        <Reveal delay={160}>
          <p className="mx-auto mt-4 max-w-xl text-base leading-relaxed text-muted">
            {contact.subheading}
          </p>
        </Reveal>

        <Reveal delay={240}>
          <div className="mt-8 flex flex-col items-center gap-4">
            <Button href={mailto} size="lg" variant="primary">
              {site.emailDisplay}
              <ArrowUpRight size={17} aria-hidden="true" />
            </Button>

            {/* Perfiles públicos (solo los que estén cargados en data/content) */}
            {site.social.length > 0 && (
              <ul className="flex flex-wrap items-center justify-center gap-x-5 gap-y-2">
                {site.social.map((profile) => (
                  <li key={profile.href}>
                    <a
                      href={profile.href}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-1.5 rounded text-sm text-muted transition-colors hover:text-ink focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent"
                    >
                      {profile.label}
                      <ArrowUpRight size={14} aria-hidden="true" />
                    </a>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </Reveal>

        <Reveal delay={320}>
          <p className="mt-5 text-sm text-faint">
            {site.role} · {site.location} · respuesta en &lt; 24 h hábiles
          </p>
        </Reveal>
      </div>
    </section>
  );
}
