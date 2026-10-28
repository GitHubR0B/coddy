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
  ShieldCheck,
  Lock,
  Eye,
  FileText,
  Info,
  Settings,
  MessageSquareText,
  Share2,
  Database,
  Baby,
  RefreshCw,
  Mail,
  KeyRound,
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
const TERMS_PATH = "/terms"; // ruta de tu página de términos
const HOSTING = "PluxHost España";
const RETENTION_DAYS = "30"; // ajusta a lo que realmente cumplas

type Lang = "es" | "en";

type Section = {
  icon: LucideIcon;
  title: string;
  p?: string[];
  list?: string[];
  after?: string[];
  extra?: "contact";
};

const fill = (s: string) =>
  s
    .replace(/\{brand\}/g, BRAND)
    .replace(/\{owner\}/g, OWNER)
    .replace(/\{hosting\}/g, HOSTING)
    .replace(/\{days\}/g, RETENTION_DAYS);

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
    termsLink: string;
    supportLink: string;
    sections: Section[];
  }
> = {
  es: {
    badge: "Escudo de privacidad v2.0",
    h1a: "Política de",
    h1b: "Privacidad.",
    back: "Volver al inicio",
    updated: "Última modificación: octubre de 2026",
    footer: "Operado por",
    termsLink: "Ver los Términos del Servicio",
    supportLink: "Servidor de soporte",
    sections: [
      {
        icon: Info,
        title: "Quiénes somos",
        p: [
          "{brand} es un bot de Discord multipropósito que ofrece moderación, protección del servidor (antinuke), automoderación, herramientas de comunidad, música, minijuegos y una función opcional de chat con IA, además de un panel web para gestionar los ajustes de cada servidor. Lo opera {owner}.",
          "Esta política explica qué información recopila el bot, cómo se usa, con quién se comparte y qué opciones tienes. Al añadir el bot a un servidor o usar sus comandos o su panel, aceptas esta política.",
        ],
      },
      {
        icon: Eye,
        title: "Recopilación de datos",
        p: [
          "El motor {brand} recopila solo lo que necesita cada función. Según las funciones que activen los administradores del servidor, puede incluir:",
        ],
        list: [
          "Identificadores de Discord: ID de usuario, de servidor, de canal, de rol y de mensaje, además de nombres de usuario y avatares, que se muestran en las respuestas del bot (tarjetas de rango, registros, mensajes de bienvenida).",
          "Configuración del servidor: prefijos, módulos activados, canales de registro, bienvenidas, autorroles, roles por reacción, tickets, verificación, listas blancas, de omisión y negras, y otros ajustes definidos por los administradores.",
          "Datos de funciones: XP, nivel y contadores de mensajes (niveles); advertencias, cárcel y silenciamientos (moderación); usuarios autorizados y acciones de protección (antinuke); quién invitó a quién (seguimiento de invitaciones); AFK, cumpleaños si el usuario lo configura, sorteos, tickets, mensajes fijos, autorrespuestas, conteo, puntuaciones de juegos y roles personalizados.",
          "Contenido de mensajes: el bot lee los mensajes para ejecutar comandos y para la automoderación y las funciones configuradas, pero no guarda un archivo general de mensajes. Las excepciones se detallan más abajo.",
          "Datos de presencia (solo si el Presence Intent está activado): leemos el estado, el dispositivo y la actividad (por ejemplo, Spotify o directos) únicamente para responder a comandos de estado y enviar las notificaciones de directos que configure un administrador. No los almacenamos.",
          "Panel web: si inicias sesión con Discord, recibimos tu ID, nombre de usuario, avatar y la lista de tus servidores para mostrarte los que puedes administrar. La sesión se mantiene con una cookie.",
          "Datos técnicos: nuestros proveedores de alojamiento y de túnel pueden procesar datos técnicos estándar, como direcciones IP y registros de peticiones, cuando se accede al panel o a su API.",
        ],
        after: [
          "No recopilamos contraseñas, datos de pago ni mensajes privados enviados a otras personas.",
        ],
      },
      {
        icon: MessageSquareText,
        title: "Excepciones sobre el contenido de mensajes",
        list: [
          "El último mensaje borrado de cada canal se guarda temporalmente en la memoria del bot para el comando «snipe». No se escribe en la base de datos y se pierde al reiniciar.",
          "Si un administrador activa el chat con IA, los mensajes enviados a la IA en ese canal se procesan para generar respuestas, y puede guardarse un historial limitado de la conversación para dar contexto.",
          "Si un administrador configura registros, el canal que elija puede recibir detalles de eventos como mensajes editados o borrados. Esos registros quedan en Discord, en el servidor del administrador.",
        ],
      },
      {
        icon: Settings,
        title: "Cómo usamos la información",
        p: ["Usamos los datos para:"],
        list: [
          "Ejecutar los comandos y las funciones que activen los administradores.",
          "Detectar y actuar ante infracciones (spam, enlaces, invitaciones, mayúsculas excesivas, menciones masivas, spam de emojis) según los ajustes del servidor.",
          "Detectar y revertir acciones maliciosas en el servidor mediante el antinuke.",
          "Dar la bienvenida, asignar roles, verificar usuarios, seguir invitaciones y registrar eventos.",
          "Calcular XP, niveles y clasificaciones, y ofrecer música y juegos.",
          "Mostrar y guardar los ajustes en el panel.",
          "Mantener el bot seguro, prevenir abusos y corregir errores.",
        ],
        after: [
          "No vendemos datos personales ni los usamos para publicidad ni para elaborar perfiles.",
        ],
      },
      {
        icon: KeyRound,
        title: "Intents privilegiados de Discord",
        p: ["El bot usa los siguientes intents privilegiados, solo para los fines indicados:"],
        list: [
          "Message Content: para leer comandos con prefijo y para la automoderación, las autorrespuestas, los mensajes fijos, el conteo, el AFK y los niveles.",
          "Server Members: para recibir eventos de entrada, salida, baneo, expulsión y actualización de miembros, necesarios para el antinuke, las bienvenidas y autorroles, el seguimiento de invitaciones, los registros y los comandos de moderación.",
          "Presence (si está activado): para las notificaciones de directos y los comandos de estado.",
        ],
      },
      {
        icon: Share2,
        title: "Servicios de terceros",
        p: ["Para funcionar, el bot se apoya en terceros que pueden procesar datos limitados:"],
        list: [
          "Discord: la plataforma donde funciona el bot, regida por su propia Política de Privacidad.",
          "Groq (chat con IA): cuando se usa la función opcional de IA, el texto del mensaje y el contexto reciente se envían a la API de Groq para generar la respuesta. No compartas información sensible con ella. Su tratamiento se rige por su propia política.",
          "Proveedores de música y Lavalink: las búsquedas y solicitudes de pistas se envían a un servidor Lavalink y a servicios como YouTube, SoundCloud o JioSaavn.",
          "Cloudflare: se usa para exponer de forma segura la API del panel por HTTPS.",
          "Alojamiento: {hosting} almacena la base de datos del bot y procesa las peticiones del panel.",
          "Vercel u otro proveedor de alojamiento web: aloja el panel.",
        ],
        after: [
          "No compartimos datos personales con ningún otro tercero, salvo obligación legal o para proteger la seguridad y los derechos de los usuarios, del bot o del público.",
        ],
      },
      {
        icon: Database,
        title: "Almacenamiento, conservación y seguridad",
        list: [
          "Los datos se guardan en una base de datos operada por nosotros en {hosting}.",
          "La configuración y los datos de funciones se conservan mientras el bot siga en el servidor, para que las funciones sigan operando.",
          "Si se saca al bot de un servidor, los datos de ese servidor se eliminan en un plazo de {days} días.",
          "Los datos generados por la actividad de un usuario (XP, advertencias, etc.) se conservan mientras sean necesarios para la función, salvo que solicite su eliminación.",
          "Los datos temporales en memoria se descartan automáticamente o al reiniciar el bot.",
        ],
        after: [
          "Aplicamos medidas técnicas razonables, como control de acceso a nuestros sistemas y claves de API en el panel. Ningún sistema es perfectamente seguro, por lo que no podemos garantizar una seguridad absoluta.",
        ],
      },
      {
        icon: FileText,
        title: "Derechos del usuario",
        p: ["Puedes:"],
        list: [
          "Pedirnos qué datos tenemos sobre ti.",
          "Pedirnos que los eliminemos (por ejemplo, XP, advertencias, AFK, cumpleaños o historial de conversaciones con la IA). Atenderemos la solicitud en un plazo razonable, salvo que debamos conservar información por motivos de seguridad, prevención de abusos o legales, o que forme parte de los registros de moderación de un servidor, de los que responden sus administradores.",
          "Dejar de usar las funciones opcionales. Los administradores pueden desactivar muchas funciones, y el chat con IA solo procesa mensajes en los canales donde se activó.",
          "Sacar al bot de tu servidor en cualquier momento.",
        ],
        after: [
          "Estas solicitudes se pueden iniciar escribiéndonos al contacto indicado al final o desde los ajustes del panel.",
          "Si estás en el Espacio Económico Europeo o en el Reino Unido, puedes tener derechos adicionales según la normativa de protección de datos: acceso, rectificación, supresión, limitación, oposición y portabilidad. Tratamos los datos con base en nuestro interés legítimo en ofrecer las funciones del bot y mantener los servidores seguros. También tienes derecho a reclamar ante tu autoridad de protección de datos.",
        ],
      },
      {
        icon: Baby,
        title: "Menores",
        p: [
          "Discord exige una edad mínima (13 años, o la que exija la ley de tu país). El bot no está dirigido a menores de esa edad y no recopilamos sus datos a sabiendas. Si crees que un menor nos ha facilitado información, contáctanos y la eliminaremos.",
        ],
      },
      {
        icon: RefreshCw,
        title: "Cambios en esta política",
        p: [
          "Podemos actualizar esta política. La fecha al pie de la página indica la última modificación. Seguir usando el bot después de un cambio implica que aceptas la política actualizada.",
        ],
      },
      {
        icon: Mail,
        title: "Contacto",
        p: ["Para preguntas o solicitudes sobre esta política o tus datos, escríbenos o únete a nuestro servidor de soporte."],
        extra: "contact",
      },
    ],
  },

  en: {
    badge: "Privacy shield v2.0",
    h1a: "Privacy",
    h1b: "Policy.",
    back: "Back to home",
    updated: "Last updated: October 2026",
    footer: "Operated by",
    termsLink: "Read the Terms of Service",
    supportLink: "Support server",
    sections: [
      {
        icon: Info,
        title: "Who we are",
        p: [
          "{brand} is a multipurpose Discord bot offering moderation, server protection (antinuke), auto-moderation, community tools, music, mini-games and an optional AI chat feature, plus a web dashboard to manage per-server settings. It is operated by {owner}.",
          "This policy explains what information the bot collects, how it is used, who it is shared with and what choices you have. By adding the bot to a server or using its commands or dashboard, you agree to this policy.",
        ],
      },
      {
        icon: Eye,
        title: "Data collection",
        p: [
          "The {brand} engine collects only what each feature needs. Depending on the features enabled by a server’s administrators, this may include:",
        ],
        list: [
          "Discord identifiers: user, server, channel, role and message IDs, plus usernames and avatars, shown in the bot’s responses (rank cards, logs, welcome messages).",
          "Server configuration: prefixes, enabled modules, log channels, welcome settings, autoroles, reaction roles, tickets, verification, whitelists, bypass lists, blacklists and other options set by administrators.",
          "Feature data: XP, level and message counters (leveling); warnings, jail records and mutes (moderation); authorized users and protective actions (antinuke); which member invited which user (invite tracking); AFK status, birthdays if a user sets one, giveaways, tickets, sticky messages, autoresponders, counting progress, game scores and custom roles.",
          "Message content: the bot reads messages to run commands and to power auto-moderation and server-configured features, but it does not keep a general archive of messages. Exceptions are listed below.",
          "Presence data (only if the Presence Intent is enabled): we read online status, device and activity (for example Spotify or streaming) only to answer status commands and to send stream notifications configured by an administrator. We do not store it.",
          "Web dashboard: if you log in with Discord, we receive your user ID, username, avatar and the list of your servers so we can show the ones you can manage. Your session is kept with a cookie.",
          "Technical data: our hosting and tunnel providers may process standard technical information, such as IP addresses and request logs, when the dashboard or its API is accessed.",
        ],
        after: [
          "We do not collect passwords, payment information, or private messages sent to other people.",
        ],
      },
      {
        icon: MessageSquareText,
        title: "Exceptions about message content",
        list: [
          "The last deleted message of each channel is kept temporarily in the bot’s memory for the “snipe” command. It is not written to a database and is lost when the bot restarts.",
          "If an administrator enables the AI chat, messages sent to the AI in that channel are processed to generate replies, and a limited conversation history may be stored to provide context.",
          "If an administrator configures logging, the channel they choose may receive details of events such as edited or deleted messages. Those logs live in Discord, in the administrator’s own server.",
        ],
      },
      {
        icon: Settings,
        title: "How we use information",
        p: ["We use data to:"],
        list: [
          "Run the commands and features that administrators enable.",
          "Detect and act on rule violations (spam, links, invites, excessive caps, mass mentions, emoji spam) according to server settings.",
          "Detect and reverse malicious actions in the server through antinuke.",
          "Welcome new members, assign roles, verify users, track invites and log events.",
          "Calculate XP, levels and leaderboards, and provide music and games.",
          "Show and save settings in the dashboard.",
          "Keep the bot secure, prevent abuse and fix errors.",
        ],
        after: [
          "We do not sell personal data, and we do not use it for advertising or profiling.",
        ],
      },
      {
        icon: KeyRound,
        title: "Discord privileged intents",
        p: ["The bot uses the following privileged intents, only for the purposes listed:"],
        list: [
          "Message Content: to read prefix commands and to run auto-moderation, autoresponders, sticky messages, counting, AFK and leveling.",
          "Server Members: to receive join, leave, ban, kick and member-update events needed for antinuke protection, welcome messages and autorole, invite tracking, logging and moderation commands.",
          "Presence (if enabled): for stream notifications and status commands.",
        ],
      },
      {
        icon: Share2,
        title: "Third-party services",
        p: ["To operate, the bot relies on third parties that may process limited data:"],
        list: [
          "Discord: the platform on which the bot runs, governed by its own Privacy Policy.",
          "Groq (AI chat): when the optional AI feature is used, the text of the message and the recent conversation context are sent to Groq’s API to generate a reply. Please do not share sensitive information with it. Its handling of data is governed by its own policy.",
          "Music providers and Lavalink: search queries and track requests are sent to a Lavalink server and to services such as YouTube, SoundCloud or JioSaavn.",
          "Cloudflare: used to securely expose the dashboard API over HTTPS.",
          "Hosting: {hosting} stores the bot’s database and processes dashboard requests.",
          "Vercel or another web host: hosts the dashboard.",
        ],
        after: [
          "We do not share personal data with any other third party, except if required by law or to protect the safety and rights of users, the bot or the public.",
        ],
      },
      {
        icon: Database,
        title: "Storage, retention and security",
        list: [
          "Data is stored in a database operated by us on {hosting}.",
          "Server configuration and feature data are kept while the bot remains in the server so the features keep working.",
          "When the bot is removed from a server, that server’s data is deleted within {days} days.",
          "Data created by a user’s own activity (XP, warnings, etc.) is kept for as long as it is needed to provide the feature, unless deletion is requested.",
          "Temporary in-memory data is discarded automatically or when the bot restarts.",
        ],
        after: [
          "We use reasonable technical measures, such as access control on our systems and API keys on the dashboard API. No system is perfectly secure, so we cannot guarantee absolute security.",
        ],
      },
      {
        icon: FileText,
        title: "User rights",
        p: ["You can:"],
        list: [
          "Ask us what data we hold about you.",
          "Ask us to delete it (for example XP, warnings, AFK, birthday data or AI conversation history). We will act on requests within a reasonable time, except where we must keep information for security, abuse-prevention or legal reasons, or where the data is part of a server’s moderation records, which its administrators are responsible for.",
          "Stop using optional features. Many features can be disabled by administrators, and the AI chat only processes messages in channels where it was enabled.",
          "Remove the bot from your server at any time.",
        ],
        after: [
          "You can start these requests by contacting us at the address at the bottom of this page or from the dashboard settings.",
          "If you are in the European Economic Area or the United Kingdom, you may have additional rights under data-protection law: access, rectification, erasure, restriction, objection and portability. We process data on the basis of our legitimate interest in providing the bot’s features and keeping servers safe. You also have the right to complain to your local data-protection authority.",
        ],
      },
      {
        icon: Baby,
        title: "Children",
        p: [
          "Discord requires a minimum age (13, or higher where your local law requires). The bot is not directed at children under that age and we do not knowingly collect their data. If you believe a child has provided us with information, contact us and we will delete it.",
        ],
      },
      {
        icon: RefreshCw,
        title: "Changes to this policy",
        p: [
          "We may update this policy from time to time. The date at the bottom of the page shows when it last changed. Continued use of the bot after a change means you accept the updated policy.",
        ],
      },
      {
        icon: Mail,
        title: "Contact",
        p: ["For questions or requests about this policy or your data, email us or join our support server."],
        extra: "contact",
      },
    ],
  },
};

/* ────────────────────────────────────────────────────────────────
 * PÁGINA
 * ──────────────────────────────────────────────────────────────── */
export default function PrivacyPage() {
  const [lang, setLang] = useState<Lang>("es");
  const t = CONTENT[lang];

  return (
    <div className="min-h-screen bg-[#150c06] text-slate-200 font-sans">
      {/* Background Decor */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none z-0">
        <div className="absolute top-[-10%] right-[-5%] w-[40%] h-[40%] bg-red-500/[0.03] blur-[120px] rounded-full" />
      </div>

      <nav className="fixed top-0 w-full z-50 border-b border-white/[0.03] bg-[#150c06]/80 backdrop-blur-3xl px-6 h-20 flex items-center justify-between">
        <Link href="/" className="flex items-center gap-4 group">
          <div className="h-9 w-9 rounded-xl bg-red-600 flex items-center justify-center mr-4">
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
              <ShieldCheck className="h-3 w-3" />
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

          <h1 className="text-5xl md:text-7xl font-bold text-white font-outfit tracking-tighter uppercase mb-12 italic">
            {t.h1a} <span className="text-red-500 not-italic">{t.h1b}</span>
          </h1>

          <div className="glass border-white/5 rounded-[40px] p-10 md:p-16 space-y-12">
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

                  {s.after?.map((para, j) => (
                    <p key={`a${j}`} className="text-slate-400 leading-relaxed font-medium">
                      {fill(para)}
                    </p>
                  ))}

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
                      <Link
                        href={TERMS_PATH}
                        className="text-red-500 hover:text-red-400 underline underline-offset-4 w-fit"
                      >
                        {t.termsLink}
                      </Link>
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