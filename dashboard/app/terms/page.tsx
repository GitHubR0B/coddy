/**
 * ╔══════════════════════════════════════════════════════════════════╗
 * ║                                                                  ║
 * ║   ░█▀▀░█▀█░█▀▄░█▀▀░█░█   ░█▀▄░█▀▀░█░█░█▀▀                     ║
 * ║   ░█░░░█░█░█░█░█▀▀░▄▀▄   ░█░█░█▀▀░▀▄▀░▀▀█                     ║
 * ║   ░▀▀▀░▀▀▀░▀▀░░▀▀▀░▀░▀   ░▀▀░░▀▀▀░░▀░░▀▀▀                     ║
 * ║                                                                  ║
 * ║           © 2026 CodeX Devs — All Rights Reserved               ║
 * ║                                                                  ║
 * ║   discord  ──  https://discord.gg/codexdev                      ║
 * ║   youtube  ──  https://youtube.com/@CodeXDevs                   ║
 * ║   github   ──  https://github.com/RayExo                        ║
 * ║                                                                  ║
 * ╚══════════════════════════════════════════════════════════════════╝
 */

"use client";

import React, { useState } from "react";
import Link from "next/link";
import type { LucideIcon } from "lucide-react";
import {
  Bot,
  ChevronLeft,
  Scale,
  Terminal,
  ShieldAlert,
  Cpu,
  Info,
  UserCheck,
  Users,
  Sparkles,
  Music,
  Ban,
  Lock,
  Copyright,
  Power,
  Gavel,
  RefreshCw,
  Globe,
  Mail,
  Languages,
} from "lucide-react";
import { Button } from "@/components/ui/button";

/* ────────────────────────────────────────────────────────────────
 * DATOS A COMPLETAR ANTES DE PUBLICAR
 * ──────────────────────────────────────────────────────────────── */
const BRAND = process.env.NEXT_PUBLIC_BRAND_NAME || "Coddy";
const OWNER = "Roberto";
const CONTACT_EMAIL = "soycoddy@gemail.com";
const SUPPORT_URL = "https://discord.gg/QzeVm6xV3";
const PRIVACY_PATH = "/privacy"; // ruta de tu página de privacidad
const GOVERNING_LAW = "España";

type Lang = "es" | "en";

type Section = {
  icon: LucideIcon;
  title: string;
  p?: string[];
  list?: string[];
  extra?: "privacy" | "contact";
};

const fill = (s: string) =>
  s
    .replace(/\{brand\}/g, BRAND)
    .replace(/\{owner\}/g, OWNER)
    .replace(/\{law\}/g, GOVERNING_LAW);

/* ────────────────────────────────────────────────────────────────
 * CONTENIDO
 * ──────────────────────────────────────────────────────────────── */
const CONTENT: Record<
  Lang,
  {
    badge: string;
    h1a: string;
    h1b: string;
    back: string;
    updated: string;
    footer: string;
    privacyLink: string;
    supportLink: string;
    sections: Section[];
  }
> = {
  es: {
    badge: "Protocolo neuronal v2.4",
    h1a: "Términos del",
    h1b: "Servicio.",
    back: "Volver al inicio",
    updated: "Octubre de 2026",
    footer: "Distribuido mediante la nube neuronal de",
    privacyLink: "Ver la Política de Privacidad",
    supportLink: "Servidor de soporte",
    sections: [
      {
        icon: Terminal,
        title: "Aceptación del protocolo",
        p: [
          "Al integrar el motor {brand} en tu servidor de Discord, usar sus comandos o iniciar sesión en el panel, aceptas cumplir estos términos. El motor se proporciona «tal cual» y, aunque nos esforzamos por alcanzar un 100 % de disponibilidad mediante nuestros clústeres perimetrales neuronales, no somos responsables de ninguna pérdida de datos derivada de interrupciones de API de terceros.",
          "Si no estás de acuerdo con estos términos, no uses el bot.",
        ],
      },
      {
        icon: UserCheck,
        title: "Elegibilidad",
        p: [
          "Debes tener la edad mínima que exige Discord (13 años, o más si lo exige la ley de tu país) y cumplir las Condiciones del Servicio y las Directrices de la Comunidad de Discord. Para añadir el bot a un servidor necesitas los permisos que Discord requiera. Si usas el bot en nombre de una comunidad u organización, confirmas que tienes autoridad para hacerlo.",
        ],
      },
      {
        icon: Info,
        title: "Qué hace {brand}",
        p: [
          "{brand} ofrece moderación, protección del servidor (antinuke), automoderación, herramientas de comunidad, música, minijuegos y una función opcional de chat con IA, además de un panel web para configurarlo todo. Las funciones pueden añadirse, cambiarse o retirarse en cualquier momento. Muchas dependen de los permisos e intents de Discord que concedas al bot.",
        ],
      },
      {
        icon: ShieldAlert,
        title: "Restricciones de uso",
        p: [
          "No puedes usar el motor {brand} para actividades ilícitas, incluidas, entre otras: el acoso automatizado, el registro de tokens o la coordinación de raids. El incumplimiento de estas restricciones provocará la desautorización neuronal inmediata y la inclusión en la lista negra de la red global de clústeres.",
          "Además, te comprometes a no:",
        ],
        list: [
          "Incumplir la ley, los términos o las directrices de Discord, ni las normas de ningún servidor.",
          "Acosar, amenazar o perjudicar a otras personas, ni usar el bot contra individuos o grupos.",
          "Intentar explotar, atacar, aplicar ingeniería inversa, sobrecargar o interrumpir el bot, su API o el panel.",
          "Abusar de comandos o funciones para hacer spam, raids o evadir la moderación y los baneos.",
          "Usar la IA para generar o pedir contenido ilegal, de odio, sexual que involucre a menores, violento o dañino, ni para compartir datos personales sensibles de terceros.",
          "Revender o redistribuir el servicio sin permiso.",
        ],
      },
      {
        icon: Users,
        title: "Responsabilidad de los administradores",
        p: [
          "Los propietarios y administradores deciden qué funciones se activan en su servidor y cómo se configuran. Son responsables de:",
        ],
        list: [
          "Elegir ajustes razonables de automoderación, antinuke, registros y sanciones.",
          "Informar a sus miembros, cuando la ley o las normas de Discord lo exijan, sobre la moderación, los registros, el seguimiento de invitaciones y cualquier otro tratamiento de datos activado.",
          "Conceder al bot solo los permisos necesarios y controlar qué personal accede a los comandos potentes y al panel.",
          "Revisar las acciones del bot. La moderación automática y el antinuke pueden equivocarse y sancionar o eliminar a la persona incorrecta.",
        ],
      },
      {
        icon: Sparkles,
        title: "Chat con IA",
        p: [
          "La función de IA es opcional y solo funciona donde los administradores la activen. Sus respuestas las genera automáticamente un modelo de terceros y pueden ser inexactas, incompletas o inapropiadas. No te fíes de ella para obtener asesoramiento legal, médico, financiero o de seguridad.",
          "Los mensajes que le envíes los procesa un proveedor de IA externo, según se explica en la Política de Privacidad, así que no compartas información personal sensible.",
        ],
      },
      {
        icon: Music,
        title: "Música y contenido de terceros",
        p: [
          "La función de música reproduce contenido de fuentes externas. No alojamos ni poseemos ese contenido y no nos hacemos responsables de él. Eres responsable de que tu uso cumpla las normas de cada plataforma y la legislación de derechos de autor aplicable. Podemos desactivar o cambiar la música en cualquier momento, por ejemplo si una fuente deja de funcionar o restringe el acceso.",
        ],
      },
      {
        icon: Cpu,
        title: "API y escalado",
        p: [
          "Nos reservamos el derecho de limitar o restringir el acceso a la API para los servidores que superen asignaciones de recursos desproporcionadas. Hay clústeres empresariales de alta escala disponibles para las comunidades que necesiten shards neuronales dedicados.",
        ],
      },
      {
        icon: Ban,
        title: "Listas negras y sanciones",
        p: [
          "Podemos restringir, incluir en la lista negra o retirar el acceso al bot a cualquier usuario o servidor que incumpla estos términos, abuse del servicio o ponga en riesgo al bot o a otros usuarios, con o sin aviso. También podemos sacar al bot de un servidor a nuestra discreción.",
        ],
      },
      {
        icon: Lock,
        title: "Privacidad",
        p: [
          "El tratamiento de tus datos se explica en nuestra Política de Privacidad. Al usar el bot, también la aceptas.",
        ],
        extra: "privacy",
      },
      {
        icon: Copyright,
        title: "Propiedad intelectual",
        p: [
          "El bot, su nombre, su marca y su contenido original pertenecen a {owner} (y a los terceros cuyos componentes de código abierto o licencias correspondan). Tú conservas la propiedad del contenido que crees. Al usar el bot, nos das el permiso limitado necesario para procesar ese contenido únicamente para ofrecer las funciones que uses.",
        ],
      },
      {
        icon: Power,
        title: "Disponibilidad y garantías",
        p: [
          "El bot es gratuito salvo que se indique lo contrario. No garantizamos que esté siempre disponible, sin interrupciones, libre de errores ni de pérdida de datos. Podemos hacer mantenimiento, cambiar o retirar funciones, o cerrar el servicio en cualquier momento.",
          "Se ofrece «tal cual» y «según disponibilidad», sin garantías de ningún tipo. No garantizamos que el antinuke, la automoderación ni ninguna otra función de protección evite todos los ataques o abusos.",
        ],
      },
      {
        icon: Gavel,
        title: "Limitación de responsabilidad",
        p: [
          "En la máxima medida permitida por la ley, no somos responsables de daños indirectos, incidentales, especiales, consecuentes o punitivos, ni de la pérdida de datos, beneficios, miembros o reputación derivada del uso del bot o de la imposibilidad de usarlo. Esto incluye los daños causados por acciones automáticas (baneos, expulsiones, borrados o cambios de roles) ejecutadas según la configuración de tu servidor.",
          "Eres responsable de tu uso del bot y de los ajustes que apliques, y te comprometes a mantenernos indemnes frente a reclamaciones derivadas del incumplimiento de estos términos, de la ley o de derechos de terceros. Nada de lo anterior excluye responsabilidades que no puedan excluirse por ley.",
        ],
      },
      {
        icon: Power,
        title: "Terminación",
        p: [
          "Puedes dejar de usar el bot en cualquier momento sacándolo de tu servidor. Podemos suspender o poner fin a tu acceso según lo descrito en estos términos. Las cláusulas que por su naturaleza deban seguir vigentes (exenciones, limitación de responsabilidad e indemnidad) continuarán aplicándose.",
        ],
      },
      {
        icon: RefreshCw,
        title: "Cambios en los términos",
        p: [
          "Podemos actualizar estos términos. La fecha al pie de la página indica la última modificación. Seguir usando el bot tras un cambio implica que aceptas los nuevos términos.",
        ],
      },
      {
        icon: Globe,
        title: "Ley aplicable",
        p: [
          "Estos términos se rigen por las leyes de {law}, sin tener en cuenta sus normas de conflicto de leyes. Los derechos imperativos de protección del consumidor de tu país no se ven afectados.",
        ],
      },
      {
        icon: Mail,
        title: "Contacto",
        p: ["Para preguntas sobre estos términos, escríbenos o únete a nuestro servidor de soporte."],
        extra: "contact",
      },
    ],
  },

  en: {
    badge: "Neural protocol v2.4",
    h1a: "Terms of",
    h1b: "Service.",
    back: "Back to home",
    updated: "October 2026",
    footer: "Distributed through the neural cloud of",
    privacyLink: "Read the Privacy Policy",
    supportLink: "Support server",
    sections: [
      {
        icon: Terminal,
        title: "Acceptance of the protocol",
        p: [
          "By adding the {brand} engine to your Discord server, using its commands or logging in to the dashboard, you agree to these terms. The engine is provided “as is” and, although we strive for 100% uptime through our neural edge clusters, we are not responsible for any data loss resulting from third-party API outages.",
          "If you do not agree with these terms, do not use the bot.",
        ],
      },
      {
        icon: UserCheck,
        title: "Eligibility",
        p: [
          "You must meet the minimum age required by Discord (13, or higher where your local law requires) and comply with Discord’s Terms of Service and Community Guidelines. To add the bot to a server you must have the permissions Discord requires for that action. If you use the bot on behalf of a community or organization, you confirm you have the authority to do so.",
        ],
      },
      {
        icon: Info,
        title: "What {brand} does",
        p: [
          "{brand} provides moderation, server protection (antinuke), auto-moderation, community tools, music, mini-games and an optional AI chat feature, along with a web dashboard to configure them. Features may be added, changed or removed at any time. Many features depend on the Discord permissions and intents you grant to the bot.",
        ],
      },
      {
        icon: ShieldAlert,
        title: "Usage restrictions",
        p: [
          "You may not use the {brand} engine for unlawful activity, including but not limited to automated harassment, token logging or raid coordination. Violating these restrictions will result in immediate neural deauthorization and blacklisting from the global cluster network.",
          "You also agree not to:",
        ],
        list: [
          "Break the law, Discord’s terms or guidelines, or the rules of any server.",
          "Harass, threaten or harm other people, or use the bot to target individuals or groups.",
          "Attempt to exploit, attack, reverse-engineer, overload or disrupt the bot, its API or the dashboard.",
          "Abuse commands or features to spam, raid, or evade moderation and bans.",
          "Use the AI feature to generate or request illegal, hateful, violent or otherwise harmful content, sexual content involving minors, or to share sensitive personal data of others.",
          "Resell or redistribute the service without permission.",
        ],
      },
      {
        icon: Users,
        title: "Server administrators’ responsibilities",
        p: [
          "Server owners and administrators decide which features are enabled in their server and how they are configured. They are responsible for:",
        ],
        list: [
          "Choosing sensible settings for auto-moderation, antinuke, logging and punishments.",
          "Informing their members, where required by law or by Discord’s rules, about moderation, logging, invite tracking and any other data processing enabled in their server.",
          "Granting the bot only the permissions it needs and controlling which staff can access powerful commands and the dashboard.",
          "Reviewing the bot’s actions. Automated moderation and antinuke can make mistakes, such as punishing or removing the wrong person.",
        ],
      },
      {
        icon: Sparkles,
        title: "AI chat",
        p: [
          "The AI feature is optional and only works where server administrators enable it. Its replies are generated automatically by a third-party model and may be inaccurate, incomplete or inappropriate. Do not rely on it for legal, medical, financial or safety-critical advice.",
          "Messages you send to it are processed by a third-party AI provider as described in the Privacy Policy, so do not share sensitive personal information with it.",
        ],
      },
      {
        icon: Music,
        title: "Music and third-party content",
        p: [
          "The music feature plays content from third-party sources. We do not host or own that content and are not responsible for it. You are responsible for making sure your use complies with the rules of each platform and with applicable copyright law. We may disable or change music features at any time, including if a source stops working or restricts access.",
        ],
      },
      {
        icon: Cpu,
        title: "API and scaling",
        p: [
          "We reserve the right to throttle or restrict API access for servers that exceed disproportionate resource allocations. High-scale enterprise clusters are available for communities that need dedicated neural shards.",
        ],
      },
      {
        icon: Ban,
        title: "Blacklists and enforcement",
        p: [
          "We may restrict, blacklist or remove access to the bot for any user or server that violates these terms, abuses the service, or puts the bot or other users at risk, with or without notice. We may also remove the bot from a server at our discretion.",
        ],
      },
      {
        icon: Lock,
        title: "Privacy",
        p: [
          "How we handle your data is explained in our Privacy Policy. By using the bot, you also agree to it.",
        ],
        extra: "privacy",
      },
      {
        icon: Copyright,
        title: "Intellectual property",
        p: [
          "The bot, its name, branding and original content belong to {owner} (and to any third parties whose open-source components or licenses apply). You keep ownership of the content you create. By using the bot, you give us the limited permission needed to process that content solely to provide the features you use.",
        ],
      },
      {
        icon: Power,
        title: "Availability and warranties",
        p: [
          "The bot is free unless stated otherwise. We do not guarantee that it will always be available, uninterrupted, error-free or free from data loss. We may carry out maintenance, change or remove features, or shut the service down at any time.",
          "It is provided “as is” and “as available”, without warranties of any kind. We do not guarantee that the antinuke, auto-moderation or any other protective feature will prevent every attack or abuse.",
        ],
      },
      {
        icon: Gavel,
        title: "Limitation of liability",
        p: [
          "To the fullest extent permitted by law, we are not liable for any indirect, incidental, special, consequential or punitive damages, or for loss of data, profits, community members or reputation, arising from your use of, or inability to use, the bot. This includes damage caused by automated actions such as bans, kicks, deletions or role changes carried out according to your server’s configuration.",
          "You are responsible for your use of the bot and for the settings you apply, and you agree to hold us harmless from claims arising from your breach of these terms, of any law or of third-party rights. Nothing above excludes liability that cannot be excluded under applicable law.",
        ],
      },
      {
        icon: Power,
        title: "Termination",
        p: [
          "You can stop using the bot at any time by removing it from your server. We may suspend or end your access as described in these terms. Sections that by their nature should survive termination (disclaimers, limitation of liability and indemnity) will continue to apply.",
        ],
      },
      {
        icon: RefreshCw,
        title: "Changes to these terms",
        p: [
          "We may update these terms from time to time. The date at the bottom of the page shows when they last changed. Continued use of the bot after a change means you accept the new terms.",
        ],
      },
      {
        icon: Globe,
        title: "Governing law",
        p: [
          "These terms are governed by the laws of {law}, without regard to conflict-of-law rules. Mandatory consumer-protection rights where you live are not affected.",
        ],
      },
      {
        icon: Mail,
        title: "Contact",
        p: ["For questions about these terms, email us or join our support server."],
        extra: "contact",
      },
    ],
  },
};

/* ────────────────────────────────────────────────────────────────
 * PÁGINA
 * ──────────────────────────────────────────────────────────────── */
export default function TermsPage() {
  const [lang, setLang] = useState<Lang>("es");
  const t = CONTENT[lang];

  return (
    <div className="min-h-screen bg-[#150c06] text-slate-200 font-sans">
      {/* Background Decor */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none z-0">
        <div className="absolute bottom-[-10%] left-[-5%] w-[40%] h-[40%] bg-red-600/[0.03] blur-[120px] rounded-full" />
      </div>

      <nav className="fixed top-0 w-full z-50 border-b border-white/[0.03] bg-[#150c06]/80 backdrop-blur-3xl px-6 h-20 flex items-center justify-between">
        <Link href="/" className="flex items-center gap-4 group">
          <div className="h-10 w-10 rounded-xl bg-red-600 flex items-center justify-center group-hover:rotate-12 transition-transform">
            <Bot className="h-5 w-5 text-white" />
          </div>
          <span className="text-xl font-bold text-white font-outfit uppercase tracking-tighter">
            {lang === "es" ? "Motor" : "Engine"} {BRAND}
          </span>
        </Link>
        <Link href="/">
          <Button variant="ghost" className="text-slate-400 hover:text-white gap-2">
            <ChevronLeft className="h-4 w-4" />
            {t.back}
          </Button>
        </Link>
      </nav>

      <main className="relative z-10 pt-40 pb-32 px-6">
        <div className="max-w-4xl mx-auto">
          <div className="flex items-center justify-between gap-4 flex-wrap mb-8">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-red-500/10 border border-red-500/20 text-red-500 text-[10px] font-black uppercase tracking-widest">
              <Scale className="h-3 w-3" />
              {t.badge}
            </div>

            {/* Selector de idioma */}
            <div
              role="group"
              aria-label="Language"
              className="inline-flex items-center gap-1 rounded-full border border-white/10 bg-white/[0.03] p-1"
            >
              <Languages className="h-3.5 w-3.5 text-slate-500 ml-2 mr-1" aria-hidden="true" />
              {(["es", "en"] as Lang[]).map((l) => (
                <button
                  key={l}
                  type="button"
                  onClick={() => setLang(l)}
                  aria-pressed={lang === l}
                  className={`px-3 py-1 rounded-full text-xs font-bold uppercase tracking-widest transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-red-500 ${
                    lang === l
                      ? "bg-red-600 text-white"
                      : "text-slate-400 hover:text-white"
                  }`}
                >
                  {l}
                </button>
              ))}
            </div>
          </div>

          <h1 className="text-5xl md:text-7xl font-bold text-white font-outfit tracking-tighter uppercase mb-12 italic text-right">
            {t.h1a} <span className="text-red-500 not-italic">{t.h1b}</span>
          </h1>

          <div className="glass border-white/5 rounded-[40px] p-10 md:p-16 space-y-12 bg-gradient-to-br from-white/[0.01] to-transparent">
            {t.sections.map((s, i) => {
              const Icon = s.icon;
              return (
                <section key={`${lang}-${i}`} className="space-y-6">
                  <div className="flex items-center gap-4 text-white">
                    <div className="h-10 w-10 shrink-0 rounded-2xl bg-white/5 border border-white/10 flex items-center justify-center text-red-500">
                      <Icon className="h-5 w-5" />
                    </div>
                    <h2 className="text-2xl font-bold font-outfit uppercase tracking-tight">
                      {fill(s.title)}
                    </h2>
                  </div>

                  {s.p?.map((para, j) => (
                    <p key={j} className="text-slate-400 leading-relaxed font-medium">
                      {fill(para)}
                    </p>
                  ))}

                  {s.list && (
                    <ul className="space-y-3 pl-1">
                      {s.list.map((item, k) => (
                        <li
                          key={k}
                          className="flex gap-3 text-slate-400 leading-relaxed font-medium"
                        >
                          <span
                            className="mt-2.5 h-1.5 w-1.5 shrink-0 rounded-full bg-red-500"
                            aria-hidden="true"
                          />
                          <span>{fill(item)}</span>
                        </li>
                      ))}
                    </ul>
                  )}

                  {s.extra === "privacy" && (
                    <Link
                      href={PRIVACY_PATH}
                      className="inline-block text-red-500 hover:text-red-400 underline underline-offset-4 font-medium"
                    >
                      {t.privacyLink}
                    </Link>
                  )}

                  {s.extra === "contact" && (
                    <div className="flex flex-col gap-2 font-medium">
                      <a
                        href={`mailto:${CONTACT_EMAIL}`}
                        className="text-red-500 hover:text-red-400 underline underline-offset-4 w-fit"
                      >
                        {CONTACT_EMAIL}
                      </a>
                      <a
                        href={SUPPORT_URL}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-red-500 hover:text-red-400 underline underline-offset-4 w-fit"
                      >
                        {t.supportLink}
                      </a>
                    </div>
                  )}
                </section>
              );
            })}

            <div className="pt-12 border-t border-white/5">
              <p className="text-[10px] font-black uppercase text-slate-600 tracking-[0.4em]">
                {t.updated}{" // "}{t.footer} {BRAND}
              </p>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}